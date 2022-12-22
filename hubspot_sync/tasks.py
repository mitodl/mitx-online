"""
Hubspot tasks
"""
import logging
import time
from math import ceil
from typing import List, Tuple

import celery
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from hubspot.crm.associations import BatchInputPublicAssociation, PublicAssociation
from hubspot.crm.objects import BatchInputSimplePublicObjectInput
from mitol.common.utils.collections import chunks
from mitol.hubspot_api.api import HubspotApi, HubspotAssociationType, HubspotObjectType
from mitol.hubspot_api.models import HubspotObject

from ecommerce.models import Order
from hubspot_sync import api
from hubspot_sync.api import get_hubspot_id_for_object
from main.celery import app
from users.models import User

log = logging.getLogger(__name__)


def max_concurrent_chunk_size(obj_count: int) -> int:
    """
    Divide number of objects by max concurrent tasks for chunk size

    Args:
        obj_count: Number of objects

    Returns:
        int: chunk size to use
    """
    return ceil(obj_count / settings.HUBSPOT_MAX_CONCURRENT_TASKS)


def batched_chunks(
    hubspot_type: str, batch_ids: List[int or (int, str)]
) -> List[List[int or str]]:
    """
    If list of ids exceed max allowed in a batch API call, chunk them up

    Args:
        hubspot_type(str): The type of hubspot object (deal, contact, etc)
        batch_ids(list): The list of object ids/emails to process

    Returns:
        list(list): List of chunked ids
    """
    max_chunk_size = 10 if hubspot_type == api.HubspotObjectType.CONTACTS.value else 100
    if len(batch_ids) <= max_chunk_size:
        return [batch_ids]
    return chunks(batch_ids, chunk_size=max_chunk_size)


@app.task
def sync_contact_with_hubspot(user_id: int) -> str:
    """
    Sync a user with a hubspot contact

    Args:
        user_id(int): The User id

    Returns:
        str: The hubspot id for the contact
    """
    return api.sync_contact_with_hubspot(user_id).id


@app.task
def sync_product_with_hubspot(bootcamp_run_id: int) -> str:
    """
    Sync a product with a hubspot product

    Args:
        bootcamp_run_id(int): The BootcampRun id

    Returns:
        str: The hubspot id for the product
    """
    return api.sync_product_with_hubspot(bootcamp_run_id).id


@app.task
def sync_deal_with_hubspot(order_id: int) -> str:
    """
    Sync an Order with a hubspot deal

    Args:
        order_id(int): The Order id

    Returns:
        str: The hubspot id for the deal
    """
    return api.sync_deal_with_hubspot(order_id).id


@app.task(acks_late=True)
def batch_upsert_hubspot_deals_chunked(ids: List[int]) -> List[str]:
    """
    Batch sync hubspot deals with matching Order ids

    Args:
        ids(list): List of object ids to process

    Returns:
        list(str): List of hubspot deal ids
    """
    results = []
    for application in Order.objects.filter(id__in=ids):
        results.append(api.sync_deal_with_hubspot(application.id).id)
        time.sleep(settings.HUBSPOT_TASK_DELAY / 1000)
    return results


@app.task(bind=True)
def batch_upsert_hubspot_deals(self, create: bool):
    """
    Batch create/update deals in hubspot

    Args:
        create(bool): Create if true, update if false
    """
    content_type = ContentType.objects.get_for_model(Order)
    synced_ids = HubspotObject.objects.filter(content_type=content_type).values_list(
        "object_id", flat=True
    )
    unsynced_ids = Order.objects.exclude(id__in=synced_ids).values_list("id", flat=True)
    object_ids = sorted(unsynced_ids if create else synced_ids)
    # Try to avoid too many consecutive tasks that could trigger rate limiting
    chunk_size = max_concurrent_chunk_size(len(object_ids))
    chunked_tasks = [
        batch_upsert_hubspot_deals_chunked.s(chunk)
        for chunk in chunks(object_ids, chunk_size=chunk_size)
    ]
    raise self.replace(celery.group(chunked_tasks))


@app.task(acks_late=True)
def batch_create_hubspot_objects_chunked(
    hubspot_type: str, ct_model_name: str, object_ids: List[int]
) -> List[str]:
    """
    Batch create or update a list of hubspot objects, no associations

    Args:
        hubspot_type(str): The hubspot object type (deal, contact, etc)
        ct_model_name(str): The corresponding model name
        object_ids: List of object ids to process

    Returns:
          list(str): list of processed hubspot ids
    """
    created_ids = []
    content_type = ContentType.objects.exclude(app_label="auth").get(
        model=ct_model_name
    )
    # Chunk again, by max allowed for object type (10 for contacts, 100 for all else)
    chunked_ids = batched_chunks(hubspot_type, object_ids)
    for chunk in chunked_ids:
        response = HubspotApi().crm.objects.batch_api.create(
            hubspot_type,
            BatchInputSimplePublicObjectInput(
                inputs=[
                    api.MODEL_FUNCTION_MAPPING[ct_model_name](obj_id)
                    for obj_id in chunk
                ]
            ),
        )
        for result in response.results:
            if ct_model_name == "user":
                object_id = (
                    User.objects.filter(
                        email__iexact=result.properties["email"], is_active=True
                    )
                    .first()
                    .id
                )
            else:
                object_id = result.properties["unique_app_id"].split("-")[-1]
            HubspotObject.objects.update_or_create(
                content_type=content_type,
                hubspot_id=result.id,
                object_id=object_id,
            )
            created_ids.append(result.id)
        time.sleep(settings.HUBSPOT_TASK_DELAY / 1000)
    return created_ids


@app.task(acks_late=True)
def batch_update_hubspot_objects_chunked(
    hubspot_type: str, ct_model_name: str, object_ids: List[Tuple[int, str]]
) -> List[str]:
    """
    Batch create or update hubspot objects, no associations

    Args:
        hubspot_type(str): The hubspot object type (deal, contact, etc)
        ct_model_name(str): The corresponding model name
        object_ids: List of (object id, hubspot id) tuples to process

    Returns:
          list(str): list of processed hubspot ids
    """
    updated_ids = []
    # Chunk again, by max allowed for object type (10 for contacts, 100 for all else)
    chunked_ids = batched_chunks(hubspot_type, object_ids)
    for chunk in chunked_ids:
        inputs = [
            {
                "id": obj_id[1],
                "properties": api.MODEL_FUNCTION_MAPPING[ct_model_name](
                    obj_id[0]
                ).properties,
            }
            for obj_id in chunk
        ]
        response = HubspotApi().crm.objects.batch_api.update(
            hubspot_type, BatchInputSimplePublicObjectInput(inputs=inputs)
        )
        updated_ids.extend([result.id for result in response.results])
        time.sleep(settings.HUBSPOT_TASK_DELAY / 1000)
    return updated_ids


@app.task(bind=True)
def batch_upsert_hubspot_objects(  # pylint:disable=too-many-arguments
    self,
    hubspot_type: str,
    model_name: str,
    app_label: str,
    create: bool = True,
    object_ids: List[int] = None,
):
    """
    Batch create or update objects in hubspot, no associations (so ideal for contacts and products)

    Args:
        hubspot_type(str): The hubspot object type (deal, contact, etc)
        model_name(str): The corresponding model name
        app_label(str): The model's containing app
        create(bool): Create if true, update if false
        object_ids(list): List of specific object ids to process if any
    """
    content_type = ContentType.objects.get_by_natural_key(app_label, model_name)
    if not object_ids:

        synced_object_ids = HubspotObject.objects.filter(
            content_type=content_type
        ).values_list("object_id", "hubspot_id")
        unsynced_objects = content_type.model_class().objects.exclude(
            id__in=[id[0] for id in synced_object_ids]
        )
        if model_name == "user":
            unsynced_objects = unsynced_objects.filter(
                is_active=True, email__contains="@"
            ).exclude(social_auth__isnull=True)
        unsynced_object_ids = unsynced_objects.values_list("id", flat=True)
        object_ids = unsynced_object_ids if create else synced_object_ids
    elif not create:
        object_ids = HubspotObject.objects.filter(
            content_type=content_type, object_id__in=object_ids
        ).values_list("object_id", "hubspot_id")
    # Limit number of chunks to avoid rate limit
    chunk_size = max_concurrent_chunk_size(len(object_ids))
    chunk_func = (
        batch_create_hubspot_objects_chunked
        if create
        else batch_update_hubspot_objects_chunked
    )
    chunked_tasks = [
        chunk_func.s(hubspot_type, model_name, chunk)
        for chunk in chunks(sorted(object_ids), chunk_size=chunk_size)
    ]
    raise self.replace(celery.group(chunked_tasks))


@app.task(acks_late=True)
def batch_upsert_associations_chunked(order_ids: List[int]):
    """
    Upsert batches of deal-contact and line-deal associations

    Args:
        order_ids(list): List of BootcampApplication IDs
    """
    contact_associations_batch = []
    line_associations_batch = []
    hubspot_client = HubspotApi()
    deal_count = len(order_ids)
    for idx, order_id in enumerate(order_ids):
        deal = Order.objects.get(id=order_id)
        contact_id = get_hubspot_id_for_object(deal.purchaser)
        deal_id = get_hubspot_id_for_object(deal)
        for line in deal.lines.iterator():
            line_id = get_hubspot_id_for_object(line)
            if contact_id and deal_id:
                contact_associations_batch.append(
                    PublicAssociation(
                        _from=deal_id,
                        to=contact_id,
                        type=HubspotAssociationType.DEAL_CONTACT.value,
                    )
                )
            if line_id and deal_id:
                line_associations_batch.append(
                    PublicAssociation(
                        _from=line_id,
                        to=deal_id,
                        type=HubspotAssociationType.LINE_DEAL.value,
                    )
                )
            if (
                len(contact_associations_batch) == 100
                or len(line_associations_batch) == 100
                or idx == deal_count - 1
            ):
                hubspot_client.crm.associations.batch_api.create(
                    HubspotObjectType.LINES.value,
                    HubspotObjectType.DEALS.value,
                    batch_input_public_association=BatchInputPublicAssociation(
                        inputs=line_associations_batch
                    ),
                )
                line_associations_batch = []
                hubspot_client.crm.associations.batch_api.create(
                    HubspotObjectType.DEALS.value,
                    HubspotObjectType.CONTACTS.value,
                    batch_input_public_association=BatchInputPublicAssociation(
                        inputs=contact_associations_batch
                    ),
                )
                contact_associations_batch = []
    return order_ids


@app.task(bind=True)
def batch_upsert_associations(self, order_ids: List[int] = None):
    """
    Upsert chunked batches of deal-contact and line-deal associations

    Args:
        order_ids(list): List of BootcampApplication IDs
    """
    deal_ids = Order.objects.all()
    if order_ids:
        deal_ids = deal_ids.filter(id__in=order_ids)
    deal_ids = deal_ids.values_list("id", flat=True)
    chunk_size = max_concurrent_chunk_size(len(deal_ids))
    chunked_tasks = [
        batch_upsert_associations_chunked.s(chunk)
        for chunk in chunks(sorted(deal_ids), chunk_size=chunk_size)
    ]
    raise self.replace(celery.group(chunked_tasks))

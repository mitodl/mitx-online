"""
Management command to sync hubspot ids to database
"""
import sys
from typing import List

from django.contrib.contenttypes.models import ContentType
from django.core.management import BaseCommand
from mitol.hubspot_api.models import HubspotObject

from ecommerce.models import Line, Order, Product
from hubspot_sync.api import (
    sync_contact_hubspot_ids_to_db,
    sync_deal_hubspot_ids_to_db,
    sync_product_hubspot_ids_to_db,
)
from users.models import User


def format_missing(missing: List[int]) -> str:
    """Return a string of missing ids"""
    return f"\n {','.join([str(id) for id in sorted(missing)])}\n\n"


class Command(BaseCommand):
    """
    Management command to sync hubspot ids to database
    """

    help = "Management command to sync hubspot ids to database"

    def sync_contacts(self):
        """
        Get hubspot ids for all Users
        """
        sys.stdout.write("Syncing user hubspot ids to database...\n")
        result = sync_contact_hubspot_ids_to_db()
        missing = User.objects.exclude(
            id__in=HubspotObject.objects.filter(
                content_type=ContentType.objects.get_for_model(User)
            ).values_list("object_id", flat=True)
        ).values_list("username", flat=True)
        if not result and missing.count() > 0:
            sys.stderr.write(
                f"Some users could not be matched with hubspot ids:\n {','.join([username for username in missing])}\n\n"
            )
        else:
            sys.stdout.write("All users matched with hubspot ids\n\n")

    def sync_products(self):
        """
        Get hubspot ids for all products
        """
        sys.stdout.write("Syncing product hubspot ids to database...\n")
        result = sync_product_hubspot_ids_to_db()
        missing = Product.objects.exclude(
            id__in=HubspotObject.objects.filter(
                content_type=ContentType.objects.get_for_model(Product)
            ).values_list("object_id", flat=True)
        ).values_list("id", flat=True)
        if not result and missing.count() > 0:
            sys.stderr.write(
                f"Some products could not be matched with hubspot ids:{format_missing(missing)}"
            )
        else:
            sys.stdout.write("All products matched with hubspot ids\n\n")

    def sync_deals(self):
        """
        Get hubspot ids for all deals and lines
        """
        sys.stdout.write("Syncing deal hubspot ids to database...\n")
        result = sync_deal_hubspot_ids_to_db()
        if not result:
            orders = Order.objects.exclude(
                id__in=HubspotObject.objects.filter(
                    content_type=ContentType.objects.get_for_model(Order)
                ).values_list("object_id", flat=True)
            ).values_list("id", flat=True)
            if orders.count() > 0:
                sys.stderr.write(
                    f"Some Orders could not be matched with hubspot ids:{format_missing(orders)}\n\n"
                )
            lines = Line.objects.exclude(
                id__in=HubspotObject.objects.filter(
                    content_type=ContentType.objects.get_for_model(Line)
                ).values_list("object_id", flat=True)
            ).values_list("id", flat=True)
            if lines.count() > 0:
                sys.stderr.write(
                    f"Some Lines could not be matched with hubspot ids:{format_missing(lines)}\n\n"
                )
        else:
            sys.stdout.write("All orders and lines matched with hubspot ids\n\n")

    def sync_all(self):
        """
        Sync all Users, Orders, Products, and Lines with Hubspot.
        """
        self.sync_contacts()
        self.sync_products()
        self.sync_deals()

    def add_arguments(self, parser):
        """
        Definition of arguments this command accepts
        """
        parser.add_argument(
            "--contacts",
            "--users",
            dest="sync_contacts",
            action="store_true",
            help="Sync all users",
        )
        parser.add_argument(
            "--products",
            dest="sync_products",
            action="store_true",
            help="Sync all products",
        )
        parser.add_argument(
            "--deals",
            "--orders",
            dest="sync_deals",
            action="store_true",
            help="Sync all orders",
        )

    def handle(self, *args, **options):
        sys.stdout.write("Syncing hubspot ids...\n")
        if not (
            options["sync_contacts"]
            or options["sync_products"]
            or options["sync_deals"]
        ):
            # If no flags are set, sync everything
            self.sync_all()
        else:
            # If some flags are set, sync the specified models
            if options["sync_contacts"]:
                self.sync_contacts()
            if options["sync_products"]:
                self.sync_products()
            if options["sync_deals"]:
                self.sync_deals()

        sys.stdout.write("Hubspot id sync complete\n")

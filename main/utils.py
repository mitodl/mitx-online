"""mitx_online utilities"""
import json
from enum import Flag, auto
from urllib.parse import quote_plus
from typing import Union, Tuple, TypeVar, Set

from django.conf import settings
from django.core.serializers import serialize
from django.http import HttpRequest
from mitol.common.utils.urls import remove_password_from_url
from mitol.common.utils.webpack import webpack_public_path
from rest_framework import status
from rest_framework.response import Response
from main import features


class FeatureFlag(Flag):
    """
    FeatureFlag enum

    Members should have values of increasing powers of 2 (1, 2, 4, 8, ...)

    """

    EXAMPLE_FEATURE = auto()


def get_js_settings(request: HttpRequest):
    """
    Get the set of JS settings

    Args:
        request (django.http.HttpRequest) the current request

    Returns:
        dict: the settings object
    """
    return {
        "gaTrackingID": settings.GA_TRACKING_ID,
        "environment": settings.ENVIRONMENT,
        "public_path": webpack_public_path(request),
        "release_version": settings.VERSION,
        "recaptchaKey": settings.RECAPTCHA_SITE_KEY,
        "sentry_dsn": remove_password_from_url(settings.SENTRY_DSN),
        "support_email": settings.EMAIL_SUPPORT,
        "site_name": settings.SITE_NAME,
        "features": {
            "upgrade_dialog": features.is_enabled(features.ENABLE_UPGRADE_DIALOG),
            "enable_discount_ui": features.is_enabled(features.ENABLE_DISCOUNT_UI),
        },
    }


def serialize_model_object(obj):
    """
    Serialize model into a dict representable as JSON
    Args:
        obj (django.db.models.Model): An instantiated Django model
    Returns:
        dict:
            A representation of the model
    """
    # serialize works on iterables so we need to wrap object in a list, then unwrap it
    data = json.loads(serialize("json", [obj]))[0]
    serialized = data["fields"]
    serialized["id"] = data["pk"]
    return serialized


def get_field_names(model):
    """
    Get field names which aren't autogenerated

    Args:
        model (class extending django.db.models.Model): A Django model class
    Returns:
        list of str:
            A list of field names
    """
    return [
        field.name
        for field in model._meta.get_fields()
        if not field.auto_created  # pylint: disable=protected-access
    ]


def encode_json_cookie_value(cookie_value: Union[dict, list, str, None]) -> str:
    """
    Encodes a JSON-compatible value to be set as the value of a cookie, which can then be decoded to get the original
    JSON value.
    """
    json_str_value = json.dumps(cookie_value)
    return quote_plus(json_str_value.replace(" ", "%20"))


def is_success_response(resp: Response) -> bool:
    return status.HTTP_200_OK <= resp.status_code < status.HTTP_300_MULTIPLE_CHOICES


T = TypeVar("T")


def get_partitioned_set_difference(
    set1: Set[T], set2: Set[T]
) -> Tuple[Set[T], Set[T], Set[T]]:
    """
    Returns a tuple containing items that only exist in the first set, items that exist in both sets, and items that
    only exist in the second set.
    """
    common_item_set = set1.intersection(set2)
    return set1 - common_item_set, common_item_set, set2 - common_item_set

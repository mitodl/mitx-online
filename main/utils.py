"""mitx_online utilities"""

import json
from datetime import datetime
from decimal import Decimal
from enum import Flag, auto
from typing import Set, Tuple, TypeVar, Union  # noqa: UP035
from urllib.parse import quote_plus

import dateutil
import pytz
from django.conf import settings
from django.core.serializers import serialize
from django.http import HttpRequest, HttpResponseRedirect
from mitol.common.utils.urls import remove_password_from_url
from rest_framework import status
from rest_framework.response import Response

from main.constants import USER_MSG_COOKIE_MAX_AGE, USER_MSG_COOKIE_NAME
from main.settings import TIME_ZONE


class FeatureFlag(Flag):
    """
    FeatureFlag enum

    Members should have values of increasing powers of 2 (1, 2, 4, 8, ...)

    """

    EXAMPLE_FEATURE = auto()


def get_js_settings(request: HttpRequest):  # noqa: ARG001
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
        "release_version": settings.VERSION,
        "recaptchaKey": settings.RECAPTCHA_SITE_KEY,
        "sentry_dsn": remove_password_from_url(settings.SENTRY_DSN),
        "support_email": settings.EMAIL_SUPPORT,
        "site_name": settings.SITE_NAME,
        "features": {},
        "posthog_api_token": settings.POSTHOG_API_TOKEN,
        "posthog_api_host": settings.POSTHOG_API_HOST,
    }


def get_refine_oidc_settings(request: HttpRequest):  # noqa: ARG001
    """
    Get the set of JS settings for refine OIDC

    Args:
        request (django.http.HttpRequest) the current request

    Returns:
        dict: the settings object
    """
    return {
        "client_id": settings.MITX_ONLINE_REFINE_OIDC_CONFIG_CLIENT_ID,
        "authority": settings.MITX_ONLINE_REFINE_OIDC_CONFIG_AUTHORITY,
        "redirect_uri": settings.MITX_ONLINE_REFINE_OIDC_CONFIG_REDIRECT_URI,
    }


def get_refine_datasources_settings(request: HttpRequest):  # noqa: ARG001
    """
    Get the set of JS settings for refine datasources

    Args:
        request (django.http.HttpRequest) the current request

    Returns:
        dict: the settings object
    """
    return {
        "mitxOnline": settings.MITX_ONLINE_REFINE_MITX_ONLINE_DATASOURCE,
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
        for field in model._meta.get_fields()  # noqa: SLF001
        if not field.auto_created  # pylint: disable=protected-access
    ]


CookieValue = Union[dict, list, str, None]


def encode_json_cookie_value(cookie_value: CookieValue) -> str:
    """
    Encodes a JSON-compatible value to be set as the value of a cookie, which can then be decoded to get the original
    JSON value.
    """
    json_str_value = json.dumps(cookie_value)
    return quote_plus(json_str_value.replace(" ", "%20"))


def redirect_with_user_message(
    redirect_uri: str, cookie_value: CookieValue
) -> HttpResponseRedirect:
    """
    Creates a redirect response with a user message

    Args:
        redirect_uri (str): the uri to redirect to
        cookie_value (CookieValue): the object to serialize into the cookie
    """
    resp = HttpResponseRedirect(redirect_uri)
    resp.set_cookie(
        key=USER_MSG_COOKIE_NAME,
        value=encode_json_cookie_value(cookie_value),
        max_age=USER_MSG_COOKIE_MAX_AGE,
    )
    return resp


def is_success_response(resp: Response) -> bool:
    return status.HTTP_200_OK <= resp.status_code < status.HTTP_300_MULTIPLE_CHOICES


T = TypeVar("T")


def get_partitioned_set_difference(
    set1: Set[T],  # noqa: UP006
    set2: Set[T],  # noqa: UP006
) -> Tuple[Set[T], Set[T], Set[T]]:  # noqa: UP006
    """
    Returns a tuple containing items that only exist in the first set, items that exist in both sets, and items that
    only exist in the second set.
    """
    common_item_set = set1.intersection(set2)
    return set1 - common_item_set, common_item_set, set2 - common_item_set


def parse_supplied_date(datearg):
    """
    Creates a datetime with timezone from a user-supplied date. For use in
    management commands.

    Args:
    - datearg (string): the date supplied by the user.
    Returns:
    - datetime
    """
    retDate = dateutil.parser.parse(datearg)
    if retDate.utcoffset() is not None:
        retDate = retDate - retDate.utcoffset()

    retDate = retDate.replace(tzinfo=pytz.timezone(TIME_ZONE))
    return retDate  # noqa: RET504


def format_decimal(amount: Decimal):
    """Return a Decimal as a formatted string with 2 decimal places"""
    return f"{amount:0.2f}"


def now_datetime_with_tz():
    """Return now with the configured timezone."""

    return datetime.now(tz=pytz.timezone(settings.TIME_ZONE))

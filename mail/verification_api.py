"""API for email verifications"""

import logging
from urllib.parse import quote_plus

from django.urls import reverse

from rest_framework import serializers

from mail import api
from mail.constants import EMAIL_CHANGE_EMAIL, EMAIL_VERIFICATION
from main.constants import USER_REGISTRATION_FAILED_MSG
from openedx.api import validate_username_email_with_edx
from openedx.exceptions import EdxApiRegistrationValidationException
from users.serializers import OPENEDX_ACCOUNT_CREATION_VALIDATION_MSGS_MAP

log = logging.getLogger()


def send_verification_email(strategy, backend, code, partial_token):  # pylint: disable=unused-argument  # noqa: ARG001
    """
    Sends a verification email for python-social-auth

    Args:
        strategy (social_django.strategy.DjangoStrategy): the strategy used to authenticate
        backend (social_core.backends.base.BaseAuth): the backend being used to authenticate
        code (social_django.models.Code): the confirmation code used to confirm the email address
        partial_token (str): token used to resume a halted pipeline
    """
    email = strategy.request_data()["email"]
    validate_email_with_edx_api(email)

    url = "{}?verification_code={}&partial_token={}".format(
        strategy.build_absolute_uri(reverse("register-confirm")),
        quote_plus(code.code),
        quote_plus(partial_token),
    )

    api.send_message(
        api.message_for_recipient(
            code.email,
            api.context_for_user(extra_context={"confirmation_url": url}),
            EMAIL_VERIFICATION,
        )
    )


def validate_email_with_edx_api(email):
    """
    Validate an email with edx api before sending a verification email

    Args:
        email (str): the email to validate
    """
    try:
        openedx_validation_msg_dict = validate_username_email_with_edx({'email': email})
    except (
        EdxApiRegistrationValidationException,
    ) as exc:
        log.exception("Unable to create user account", exc)  # noqa: PLE1205, TRY401
        raise serializers.ValidationError(USER_REGISTRATION_FAILED_MSG)  # noqa: B904
    if openedx_validation_msg_dict["email"]:
        # there is no email form field at this point, but we are still validating the email address
        raise serializers.ValidationError({
                "email": OPENEDX_ACCOUNT_CREATION_VALIDATION_MSGS_MAP.get(
                    openedx_validation_msg_dict["email"]
                )
            })


def send_verify_email_change_email(request, change_request):
    """
    Sends a verification email for a user email change
    Args:
        request (django.http.Request): the http request we're sending this email for
        change_request (ChangeEmailRequest): the change request to send the confirmation for
    """

    url = "{}?verification_code={}".format(
        request.build_absolute_uri(reverse("account-confirm-email-change")),
        quote_plus(change_request.code),
    )

    api.send_messages(
        list(
            api.messages_for_recipients(
                [
                    (
                        change_request.new_email,
                        api.context_for_user(extra_context={"confirmation_url": url}),
                    )
                ],
                EMAIL_CHANGE_EMAIL,
            )
        )
    )

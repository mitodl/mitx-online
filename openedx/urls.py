"""Courseware urls"""

from django.urls import path

from openedx import views

urlpatterns = (
    path(
        "login/_private/complete",
        views.openedx_private_auth_complete,
        name="openedx-private-oauth-complete",
    ),
)

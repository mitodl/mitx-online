"""Courseware factories"""

from datetime import timedelta

import pytz
from factory import Faker, LazyAttribute, SubFactory, Trait
from factory.django import DjangoModelFactory
from mitol.common.utils import now_in_utc

from openedx.constants import PLATFORM_EDX
from openedx.models import OpenEdxApiAuth, OpenEdxUser


class OpenEdxUserFactory(DjangoModelFactory):
    """Factory for OpenEdxUser"""

    user = SubFactory("users.factories.UserFactory")
    platform = PLATFORM_EDX
    has_been_synced = True

    class Meta:
        model = OpenEdxUser


class OpenEdxApiAuthFactory(DjangoModelFactory):
    """Factory for OpenEdxApiAuth"""

    user = SubFactory("users.factories.UserFactory")
    refresh_token = Faker("pystr", max_chars=30)
    access_token = Faker("pystr", max_chars=30)
    access_token_expires_on = Faker("future_datetime", end_date="+10h", tzinfo=pytz.utc)

    class Meta:
        model = OpenEdxApiAuth

    class Params:
        expired = Trait(
            access_token_expires_on=LazyAttribute(
                lambda _: now_in_utc() - timedelta(days=1)
            )
        )

"""
Un-Retire user from MITx Online
"""

import sys
from argparse import RawTextHelpFormatter
from urllib.parse import urlparse

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from social_django.models import UserSocialAuth
from user_util import user_util

from authentication.utils import block_user_email
from main import settings
from openedx.api import bulk_retire_edx_users
from users.api import fetch_users

User = get_user_model()


class Command(BaseCommand):
    """
    Retire user from MITx Online
    """

    help = """
    Un-retire one user. Username or retired email can be used to identify a user.

    For single user use:\n
    `./manage.py retire_users --user=foo` or do \n
    `./manage.py retire_users -u foo` \n or do \n
    `./manage.py retire_users -u foo@email.com` \n or do \n
    """

    def create_parser(self, prog_name, subcommand):  # pylint: disable=arguments-differ
        """
        create parser to add new line in help text.
        """
        parser = super().create_parser(prog_name, subcommand)
        parser.formatter_class = RawTextHelpFormatter
        return parser

    def add_arguments(self, parser):
        """Parse arguments"""

        # pylint: disable=expression-not-assigned
        parser.add_argument(
            "-u",
            "--user",
            action="append",
            default=[],
            dest="user",
            help="Single username or email",
        )

    def handle(self, *args, **kwargs):  # noqa: ARG002
        user = kwargs.get("user", [])

        if not user:
            self.stderr.write(
                self.style.ERROR(
                    "No user(s) provided. Please provide user(s) using -u or --user."
                )
            )
            sys.exit(1)

        user = fetch_users(kwargs["user"])


            resp = bulk_retire_edx_users(user.username)
            if user.username not in resp["successful_user_retirements"]:
                self.stderr.write(
                    self.style.ERROR(
                        f"Could not initiate retirement request on edX for user {user}"
                    )
                )
                continue
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Retirement request initiated on edX for User: '{user}'"
                    )
                )

            user.is_active = True

            # Change user password & email
            email = user.email

            user.email = self.get_retired_email(user.email)
            user.set_unusable_password()
            user.save()

            self.stdout.write(
                f"Email changed from {email} to {user.email} and password is not useable now"
            )

            # reset user social auth
            auth_deleted_count = UserSocialAuth.objects.filter(user=user).delete()

            if auth_deleted_count:
                self.stdout.write(f"For  user: '{user}' SocialAuth rows deleted")

            self.stdout.write(
                self.style.SUCCESS(f"User: '{user}' is retired from MITx Online")
            )

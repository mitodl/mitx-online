# Generated by Django 3.2.18 on 2023-02-28 18:35

from django.db import migrations


def add_user_profiles(apps, schema_editor):
    """Adds user profiles to existing accounts."""

    User = apps.get_model("users", "User")
    UserProfile = apps.get_model("users", "UserProfile")

    for user in User.objects.all():
        if UserProfile.objects.filter(user=user).count() == 0:
            UserProfile(user=user).save()


def reverse_user_profiles(apps, schema_editor):
    """No-op (no reversal for empty user profile records - no harm in keeping them)"""
    return


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0021_alter_user_name_limit"),
    ]

    operations = [migrations.RunPython(add_user_profiles, reverse_user_profiles)]

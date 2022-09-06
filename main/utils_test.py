"""Utils tests"""
from mitol.common.utils.urls import remove_password_from_url

from main.models import AuditModel
from main.utils import get_field_names, get_js_settings, get_partitioned_set_difference


def test_get_field_names():
    """
    Assert that get_field_names does not include related fields
    """
    assert set(get_field_names(AuditModel)) == {
        "data_before",
        "data_after",
        "acting_user",
        "created_on",
        "updated_on",
    }


def test_get_js_settings(settings, rf):
    """Test get_js_settings"""
    settings.GA_TRACKING_ID = "fake"
    settings.ENVIRONMENT = "test"
    settings.VERSION = "4.5.6"
    settings.EMAIL_SUPPORT = "support@text.com"
    settings.RECAPTCHA_SITE_KEY = "fake_key"
    settings.ENABLE_UPGRADE_DIALOG = False
    settings.DISABLE_DISCOUNT_UI = False
    settings.ENABLE_PROGRAM_UI = False

    request = rf.get("/")

    assert get_js_settings(request) == {
        "gaTrackingID": "fake",
        "environment": settings.ENVIRONMENT,
        "sentry_dsn": remove_password_from_url(settings.SENTRY_DSN),
        "release_version": settings.VERSION,
        "recaptchaKey": settings.RECAPTCHA_SITE_KEY,
        "support_email": settings.EMAIL_SUPPORT,
        "site_name": settings.SITE_NAME,
        "features": {
            "upgrade_dialog": settings.ENABLE_UPGRADE_DIALOG,
            "disable_discount_ui": settings.DISABLE_DISCOUNT_UI,
            "enable_program_ui": settings.ENABLE_PROGRAM_UI,
        },
    }


def test_get_partitioned_set_difference():
    """
    get_partitioned_set_difference should return a tuple with unique and common items between two sets
    """
    set1 = {1, 2, 3, 4}
    set2 = {3, 4, 5, 6}
    assert get_partitioned_set_difference(set1, set2) == ({1, 2}, {3, 4}, {5, 6})
    set2 = {3, 4}
    assert get_partitioned_set_difference(set1, set2) == ({1, 2}, {3, 4}, set())

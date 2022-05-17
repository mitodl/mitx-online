"""
Admin views for flexible pricing app
"""

from django.contrib import admin
from reversion.admin import VersionAdmin

from flexiblepricing.models import (
    CountryIncomeThreshold,
    FlexiblePrice,
)


class CountryIncomeThresholdAdmin(admin.ModelAdmin):
    """Admin for CountryIncomeThreshold"""

    model = CountryIncomeThreshold
    list_display = ("country_code", "income_threshold")
    ordering = ("country_code",)


@admin.register(FlexiblePrice)
class FlexiblePriceAdmin(VersionAdmin):
    """Admin for FlexiblePrice"""

    model = FlexiblePrice
    raw_id_fields = ("user",)

    def has_delete_permission(
        self, *args, **kwargs
    ):  # pylint: disable=unused-argument, signature-differs
        return False

    def save_model(self, request, obj, form, change):
        """
        Saves object and logs change to object
        """
        obj.save_and_log(request.user)


admin.site.register(CountryIncomeThreshold, CountryIncomeThresholdAdmin)

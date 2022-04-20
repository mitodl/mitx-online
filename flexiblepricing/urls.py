from django.urls import include, re_path
from rest_framework_extensions.routers import NestedRouterMixin
from rest_framework.routers import SimpleRouter

from flexiblepricing.views.v0 import (
    CurrencyExchangeRateViewSet,
    CountryIncomeThresholdViewSet,
    FlexiblePriceViewSet,
    FlexiblePriceAdminViewSet,
)


class SimpleRouterWithNesting(NestedRouterMixin, SimpleRouter):
    pass


router = SimpleRouterWithNesting()
router.register(
    r"exchange_rates", CurrencyExchangeRateViewSet, basename="fp_exchangerates_api"
)
router.register(
    r"income_thresholds",
    CountryIncomeThresholdViewSet,
    basename="fp_countryincomethresholds_api",
)
router.register(
    r"applications", FlexiblePriceViewSet, basename="fp_flexiblepricing_api"
)
router.register(
    r"applications_admin",
    FlexiblePriceAdminViewSet,
    basename="fp_admin_flexiblepricing_api",
)

urlpatterns = [
    re_path(r"^api/v0/flexible_pricing/", include(router.urls)),
    re_path(r"^api/flexible_pricing/", include(router.urls)),
]

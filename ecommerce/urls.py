from django.urls import include, path, re_path
from rest_framework.routers import SimpleRouter
from rest_framework_extensions.routers import NestedRouterMixin

""" TODO: clean this up later (make the views look more like the courses one) """
from ecommerce.admin import AdminRefundOrderView  # noqa: E402
from ecommerce.views.v0 import (  # noqa: E402
    AllProductViewSet,
    BackofficeCallbackView,
    BasketDiscountViewSet,
    BasketItemViewSet,
    BasketViewSet,
    CheckoutApiViewSet,
    CheckoutCallbackView,
    CheckoutInterstitialView,
    CheckoutProductView,
    DiscountViewSet,
    NestedDiscountProductViewSet,
    NestedDiscountRedemptionViewSet,
    NestedDiscountTierViewSet,
    NestedUserDiscountViewSet,
    OrderHistoryViewSet,
    OrderReceiptView,
    ProductViewSet,
    UserDiscountViewSet,
)


class SimpleRouterWithNesting(NestedRouterMixin, SimpleRouter):
    pass


router = SimpleRouterWithNesting()
router.register(r"products/all", AllProductViewSet, basename="all_products_api")
router.register(r"products", ProductViewSet, basename="products_api")
router.register(r"checkout", CheckoutApiViewSet, basename="checkout_api")
router.register(r"orders/history", OrderHistoryViewSet, basename="orderhistory_api")
router.register(r"discounts/user", UserDiscountViewSet, basename="userdiscounts_api")

discountsRouter = router.register(  # noqa: N816
    r"discounts", DiscountViewSet, basename="discounts_api"
)
discountsRouter.register(
    r"redemptions",
    NestedDiscountRedemptionViewSet,
    basename="discounts_api-redemptions",
    parents_query_lookups=["redeemed_discount"],
)
discountsRouter.register(
    r"assignees",
    NestedUserDiscountViewSet,
    basename="discounts_api-assignees",
    parents_query_lookups=["discount"],
)
discountsRouter.register(
    r"products",
    NestedDiscountProductViewSet,
    basename="discounts_api-products",
    parents_query_lookups=["discount"],
)
discountsRouter.register(
    r"tiers",
    NestedDiscountTierViewSet,
    basename="discounts_api-tiers",
    parents_query_lookups=["discount"],
)

basketRouter = router.register(r"baskets", BasketViewSet, basename="basket")  # noqa: N816
basketRouter.register(
    r"items",
    BasketItemViewSet,
    basename="basket-items",
    parents_query_lookups=["basket"],
)
basketRouter.register(
    r"discounts",
    BasketDiscountViewSet,
    basename="basket-discounts",
    parents_query_lookups=["basket"],
)

urlpatterns = [
    path("api/v0/", include(router.urls)),
    path("api/", include(router.urls)),
    re_path(
        "checkout/to_payment",
        CheckoutInterstitialView.as_view(),
        name="checkout_interstitial_page",
    ),
    path(
        "api/orders/receipt/<int:pk>/",
        OrderReceiptView.as_view(),
        name="order_receipt_api",
    ),
    re_path(
        r"^api/checkout/result/",
        BackofficeCallbackView.as_view(),
        name="checkout_result_api",
    ),
    re_path(
        r"^checkout/result/",
        CheckoutCallbackView.as_view(),
        name="checkout-result-callback",
    ),
    re_path(r"^cart/add", CheckoutProductView.as_view(), name="checkout-product"),
    re_path(r"^int_admin/refund", AdminRefundOrderView.as_view(), name="refund-order"),
]

"""Admin management for Ecommerce module"""

from django.contrib import admin, messages
from django.contrib.admin.decorators import display
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView
from mitol.common.admin import TimestampedModelAdmin
from reversion.admin import VersionAdmin
from viewflow import fsm

from ecommerce.api import refund_order
from ecommerce.forms import AdminRefundOrderForm
from ecommerce.models import (
    Basket,
    BasketDiscount,
    BasketItem,
    CanceledOrder,
    Discount,
    DiscountProduct,
    DiscountRedemption,
    FulfilledOrder,
    Line,
    Order,
    OrderFlow,
    OrderStatus,
    PendingOrder,
    Product,
    RefundedOrder,
    Transaction,
    UserDiscount,
)


@admin.register(Transaction)
class TransactionAdmin(VersionAdmin):
    """Admin for Product"""

    model = Transaction
    raw_id_fields = ("order",)


@admin.register(Product)
class ProductAdmin(VersionAdmin):
    """Admin for Product"""

    model = Product
    search_fields = (
        "description",
        "courserunproducts__title",
        "programruns__program__title",
        "courserunproducts__courseware_id",
        "programruns__program__readable_id",
    )
    list_display = ("id", "content_object", "description", "price", "is_active")
    list_filter = ("content_type", "is_active")

    def change_view(self, request, object_id, form_url="", extra_context=None):
        product = Product.objects.get(id=object_id)
        extra_context = {"subtitle": self.content_object(product)}
        return super(ProductAdmin, self).change_view(  # noqa: UP008
            request, object_id, form_url, extra_context
        )

    def content_object(self, obj):
        """Return the content object details"""
        return str(obj.purchasable_object)

    def has_delete_permission(self, request, obj=None):  # noqa: ARG002
        """Disable the delete permission for Product models"""
        return False

    def get_queryset(self, request):  # noqa: ARG002
        """
        Return the all objects for the Product Admin
        """
        return self.model.all_objects.get_queryset()


@admin.register(Basket)
class BasketAdmin(VersionAdmin):
    """Admin for Basket"""

    model = Basket
    search_fields = ["user__email", "user__username"]
    list_display = ["id", "user"]
    raw_id_fields = ("user",)


@admin.register(BasketItem)
class BasketItemAdmin(VersionAdmin):
    """Admin for BasketItem"""

    model = BasketItem
    search_fields = ["product__description", "product__price"]
    list_display = ["id", "product", "quantity"]
    raw_id_fields = ("basket", "product")


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    model = Discount
    search_fields = ["discount_type", "redemption_type", "discount_code"]
    list_display = [
        "id",
        "discount_code",
        "discount_type",
        "amount",
        "redemption_type",
        "payment_type",
    ]
    list_filter = ["discount_type", "redemption_type", "payment_type"]


@admin.register(DiscountProduct)
class DiscountProductAdmin(admin.ModelAdmin):
    model = DiscountProduct
    search_fields = [
        "discount__discount_type",
        "discount__redemption_type",
        "product__description",
        "product__price",
    ]
    list_display = ["id", "discount", "product"]
    raw_id_fields = ("discount", "product")


@admin.register(UserDiscount)
class UserDiscountAdmin(admin.ModelAdmin):
    model = UserDiscount
    search_fields = [
        "discount__discount_type",
        "discount__redemption_type",
        "user__name",
        "user__email",
        "user__username",
    ]
    list_display = ["id", "discount", "user"]
    raw_id_fields = ("discount", "user")


@admin.register(DiscountRedemption)
class DiscountRedemptionAdmin(admin.ModelAdmin):
    model = DiscountRedemption
    search_fields = [
        "redeemed_discount__discount_code",
        "redeemed_by__email",
        "redeemed_by__username",
        "redeemed_order__reference_number",
    ]
    list_display = [
        "id",
        "redemption_date",
        "redeemed_discount",
        "redeemed_by",
        "redeemed_order",
    ]
    readonly_fields = (
        "redemption_date",
        "redeemed_discount",
        "redeemed_by",
        "redeemed_order",
    )


@admin.register(BasketDiscount)
class BasketDiscountAdmin(admin.ModelAdmin):
    model = BasketDiscount
    list_display = ["id", "redeemed_basket", "redeemed_discount"]
    raw_id_fields = ("redeemed_basket", "redeemed_discount", "redeemed_by")


class OrderLineInline(admin.TabularInline):
    """Inline editor for lines"""

    model = Line
    readonly_fields = ["unit_price", "total_price", "discounted_price"]
    min_num = 1
    extra = 0


class OrderDiscountInline(admin.TabularInline):
    """Inline editor for DiscountRedemptions in an Order"""

    model = DiscountRedemption
    readonly_fields = ["redemption_date", "redeemed_by", "redeemed_discount"]
    min_num = 0
    extra = 0


class OrderTransactionInline(admin.TabularInline):
    """Inline editor for transactions for an Order"""

    def has_add_permission(self, request, obj=None):  # noqa: ARG002
        return False

    model = Transaction
    readonly_fields = ["order", "amount", "data"]
    min_num = 0
    extra = 0
    can_delete = False
    can_add = False


class BaseOrderAdmin(fsm.FlowAdminMixin, TimestampedModelAdmin):
    """Base admin for Order"""

    search_fields = [
        "id",
        "purchaser__email",
        "purchaser__username",
        "reference_number",
    ]
    list_display = ["id", "state", "get_purchaser", "total_price_paid"]
    list_fields = ["state"]
    list_filter = ["state"]
    inlines = [OrderLineInline, OrderDiscountInline, OrderTransactionInline]
    readonly_fields = ["reference_number"]
    flow_state = OrderFlow.state
    
    def get_transition_fields(self, request, obj, slug):
        return ['state']
    
    def get_object_flow(self, request, obj):
        return OrderFlow(
            obj, user=request.user
        )

    def has_change_permission(self, request, obj=None):  # noqa: ARG002
        return False

    @display(description="Purchaser")
    def get_purchaser(self, obj: Order):
        return f"{obj.purchaser.name} ({obj.purchaser.email})"

    def get_queryset(self, request):
        """Filter only to pending orders"""
        return (
            super()
            .get_queryset(request)
            .prefetch_related("purchaser", "lines__product_version")
        )


@admin.register(Order)
class OrderAdmin(BaseOrderAdmin):
    """Admin for Order"""

    list_display = ["id", "state", "purchaser", "total_price_paid", "reference_number"]
    model = Order


@admin.register(PendingOrder)
class PendingOrderAdmin(BaseOrderAdmin):
    """Admin for PendingOrder"""

    model = PendingOrder

    def get_queryset(self, request):
        """Filter only to pending orders"""
        return super().get_queryset(request).filter(state=OrderStatus.PENDING)


@admin.register(CanceledOrder)
class CanceledOrderAdmin(BaseOrderAdmin):
    """Admin for CanceledOrder"""

    model = CanceledOrder

    def get_queryset(self, request):
        """Filter only to canceled orders"""
        return super().get_queryset(request).filter(state=OrderStatus.CANCELED)


@admin.register(FulfilledOrder)
class FulfilledOrderAdmin(TimestampedModelAdmin):
    """Admin for FulfilledOrder"""

    readonly_fields = ["reference_number"]
    search_fields = [
        "id",
        "purchaser__email",
        "purchaser__username",
        "reference_number",
    ]
    list_display = ["id", "state", "get_purchaser", "total_price_paid"]
    list_fields = ["state"]
    list_filter = ["state"]
    inlines = [OrderLineInline, OrderDiscountInline, OrderTransactionInline]
    model = FulfilledOrder

    def has_change_permission(self, request, obj=None):  # noqa: ARG002
        return False

    @display(description="Purchaser")
    def get_purchaser(self, obj: Order):
        return f"{obj.purchaser.name} ({obj.purchaser.email})"

    def get_queryset(self, request):
        """Filter only to fulfilled orders"""
        return (
            super()
            .get_queryset(request)
            .prefetch_related("purchaser", "lines__product_version")
            .filter(state=OrderStatus.FULFILLED)
        )

    def response_change(self, request, obj):
        if "refund" in request.POST:
            return HttpResponseRedirect(
                "%s/?order=%s" % (reverse("refund-order"), obj.id)  # noqa: UP031
            )

        return super().response_change(request, obj)


@admin.register(RefundedOrder)
class RefundedOrderAdmin(BaseOrderAdmin):
    """Admin for RefundedOrder"""

    model = RefundedOrder

    def get_queryset(self, request):
        """Filter only to refunded orders"""
        return super().get_queryset(request).filter(state=OrderStatus.REFUNDED)


class AdminRefundOrderView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = "refund_order_confirm.html"
    permission_required = "is_superuser"

    def post(self, request):
        try:
            refund_form = AdminRefundOrderForm(request.POST)
            order = FulfilledOrder.objects.get(pk=request.POST["order"])

            if refund_form.is_valid():
                should_unenroll = refund_form.cleaned_data.get(
                    "perform_unenrolls", False
                )
                refund_reason = refund_form.cleaned_data.get("refund_reason")
                refund_amount = refund_form.cleaned_data.get("refund_amount")

                # Call the refund CyberSource API with provided reason and amount
                refund_api_success, _ = refund_order(
                    order_id=order.id,
                    refund_amount=refund_amount,
                    refund_reason=refund_reason,
                    unenroll=should_unenroll,
                )

                if not refund_api_success:
                    messages.error(
                        request, f"Order {order.reference_number} refund failed."
                    )

                elif refund_api_success and should_unenroll:
                    messages.success(
                        request,
                        f"Order {order.reference_number} refunded and unenrollment is in progress.",
                    )
                elif refund_api_success:
                    messages.success(
                        request, f"Order {order.reference_number} refunded."
                    )

                return HttpResponseRedirect(
                    reverse("admin:ecommerce_refundedorder_change", args=(order.id,))
                )

            errors = []
            error_messages = {}

            for refund_error in refund_form.errors:
                errors.append(refund_error)
                error_messages[refund_error] = refund_form.errors[refund_error]

            return render(
                request,
                self.template_name,
                {
                    "refund_form": refund_form,
                    "order": order,
                    "form_valid": refund_form.is_valid(),
                    "errors": errors,
                    "error_messages": error_messages,
                },
            )
        except NotImplementedError:
            messages.error(request, f"Order {request.POST['order']} can't be refunded.")
            return HttpResponseRedirect(
                reverse("admin:ecommerce_refundedorder_changelist")
            )
        except ObjectDoesNotExist:
            messages.error(
                request,
                f"Order {request.POST['order']} could not be found - is it Fulfilled?",
            )
            return HttpResponseRedirect(
                reverse("admin:ecommerce_fulfilledorder_changelist")
            )

    def get(self, request):
        try:
            order = FulfilledOrder.objects.get(pk=request.GET["order"])
            if order.state != OrderStatus.FULFILLED:
                raise ObjectDoesNotExist()  # noqa: RSE102, TRY301
        except ObjectDoesNotExist:
            messages.error(
                request,
                f"Order {request.GET['order']} could not be found - is it Fulfilled?",
            )
            return HttpResponseRedirect(
                reverse("admin:ecommerce_fulfilledorder_changelist")
            )

        refund_form = AdminRefundOrderForm(
            initial={
                "_selected_action": order.id,
                "refund_amount": order.total_price_paid,
            }
        )

        return render(
            request,
            self.template_name,
            {
                "refund_form": refund_form,
                "order": order,
                "form_valid": True,
                "errors": {},
            },
        )

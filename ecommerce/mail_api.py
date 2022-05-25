"""Ecommerce mail functions"""
import pycountry
import logging

from ecommerce.messages import OrderReceiptMessage
from mitol.mail.api import get_message_sender

log = logging.getLogger()


def send_ecommerce_order_receipt(order):
    """
    Send emails receipt summarizing the user purchase detail.

    Args:
        order: An order.
    """
    from ecommerce.serializers import OrderReceiptSerializer

    data = OrderReceiptSerializer(instance=order).data
    purchaser = data.get("purchaser")
    coupon = data.get("coupon")
    lines = data.get("lines")
    order = data.get("order")
    receipt = data.get("receipt")
    country = pycountry.countries.get(alpha_2=purchaser.get("country"))
    recipient = purchaser.get("email")

    try:
        with get_message_sender(OrderReceiptMessage) as sender:
            sender.build_and_send_message(
                recipient,
                {
                    "coupon": coupon,
                    "content_title": lines[0].get("content_title") if lines else None,
                    "lines": lines,
                    "order_total": format(
                        sum(float(line["total_paid"]) for line in lines),
                        ".2f",
                    ),
                    "order": order,
                    "receipt": receipt,
                    "purchaser": {
                        "name": " ".join(
                            [
                                purchaser.get("first_name"),
                                purchaser.get("last_name"),
                            ]
                        ),
                        "email": purchaser.get("email"),
                        "street_address": purchaser.get("street_address"),
                        "state_code": purchaser.get("state_or_territory").split("-")[
                            -1
                        ],
                        "postal_code": purchaser.get("postal_code"),
                        "city": purchaser.get("city"),
                        "country": country.name if country else None,
                        "company": purchaser.get("company"),
                    },
                },
            )

    except:  # pylint: disable=bare-except
        log.exception("Error sending order receipt email.")

import pytest
import random

from ecommerce.models import BasketItem
from main.test_utils import assert_drf_json_equal
from django.urls import reverse
import operator as op

from ecommerce.serializers import (
    ProductSerializer,
    BasketSerializer,
    BasketItemSerializer,
)
from ecommerce.factories import ProductFactory, BasketItemFactory

pytestmark = [pytest.mark.django_db]


@pytest.fixture()
def products():
    return ProductFactory.create_batch(5)


def test_list_products(user_drf_client, products):
    resp = user_drf_client.get(reverse("products_api-list"), {"l": 10, "o": 0})
    resp_products = sorted(resp.json()["results"], key=op.itemgetter("id"))

    assert len(resp_products) == len(products)

    for product, resp_product in zip(products, resp_products):
        assert_drf_json_equal(resp_product, ProductSerializer(product).data)


def test_get_products(user_drf_client, products):
    product = products[random.randrange(0, len(products))]

    resp = user_drf_client.get(
        reverse("products_api-detail", kwargs={"pk": product.id})
    )

    assert_drf_json_equal(resp.json(), ProductSerializer(product).data)


def test_get_basket(user_drf_client):
    """Test the view that returns a state of Basket"""
    basket_item = BasketItemFactory.create()
    basket = basket_item.basket
    resp = user_drf_client.get(reverse("basket-detail", kwargs={"pk": basket.id}))
    assert_drf_json_equal(resp.json(), BasketSerializer(basket).data)


def test_get_basket_items(user_drf_client):
    """Test the view that returns a list of BasketItems in a Basket"""
    basket_item = BasketItemFactory.create()
    basket = basket_item.basket
    basket_item_2 = BasketItemFactory.create(basket=basket)
    # this item belongs to another basket, and should not be in the response
    BasketItemFactory.create()
    resp = user_drf_client.get("/api/baskets/{}/items".format(basket.id), follow=True)
    basket_info = resp.json()
    assert len(basket_info) == 2
    assert_drf_json_equal(
        resp.json(),
        [
            BasketItemSerializer(basket_item).data,
            BasketItemSerializer(basket_item_2).data,
        ],
    )


def test_delete_basket_item(user_drf_client):
    """Test the view to delete item from the basket"""
    basket_item = BasketItemFactory.create()
    basket = basket_item.basket
    assert basket.basket_items.count() == 1
    user_drf_client.delete(
        "/api/baskets/{}/items/{}/".format(basket.id, basket_item.id),
        content_type="application/json",
    )
    assert BasketItem.objects.filter(basket=basket).count() == 0


def test_add_basket_item(user_drf_client):
    """Test the view to add a new item into the Basket"""
    basket_item = BasketItemFactory.create()
    basket = basket_item.basket
    assert basket.basket_items.count() == 1
    new_product = ProductFactory.create()
    resp = user_drf_client.post(
        "/api/baskets/{}/add_item".format(basket.id),
        data={"product_id": new_product.id},
        follow=True,
    )
    print(resp)
    assert BasketItem.objects.filter(basket=basket).count() == 2

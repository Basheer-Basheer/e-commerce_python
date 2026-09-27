from exceptions.exceptions_modules import InvalidProductStatusError
from order_item.order_item_module import OrderItem
import pytest
from pytest import fixture
from decimal import Decimal

from product.product_model import Product, ProductCategoryEnum, ProductStatusEnum


@fixture
def product():
    return Product(
        name="Mouse",
        stock=15,
        description="New moues",
        category=ProductCategoryEnum.ELECTRONICS,
        price=150,
    )


def test_order_item_creation(product):
    item = OrderItem(
        product=product,
        quantity=2,

    )

    assert item.product is product
    assert item.quantity == 2
    assert item.unit_price == product.price


def test_order_item_generates_uuid(product):
    item = OrderItem(
        product=product,
        quantity=2,

    )

    assert item.order_item_id is not None


def test_order_item_generates_uuid(product):
    item = OrderItem(
        product=product,
        quantity=2,

    )

    assert item.order_item_id is not None


def test_order_item_quantity_must_be_integer(product):
    with pytest.raises(TypeError):
        OrderItem(
            product=product,
            quantity=2.5,

        )


def test_order_item_quantity_must_be_positive(product):
    with pytest.raises(ValueError):
        OrderItem(
            product=product,
            quantity=0,

        )


def test_order_item_subtotal(product):
    item = OrderItem(
        product=product,
        quantity=2,
    )

    assert item.subtotal() == Decimal("300.00")


def test_order_item_uses_product_price(product):
    item = OrderItem(
        product=product,
        quantity=2,
    )

    assert item.unit_price == product.price


def test_product_decrease_stock_fails_when_discontinued(product):
    product.discontinue()
    with pytest.raises(InvalidProductStatusError):
        product.decrease_stock(5)

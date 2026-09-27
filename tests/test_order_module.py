import pytest
from decimal import Decimal

from customer.customer_model import Customer
from product.product_model import Product, ProductCategoryEnum
from order_item.order_item_module import OrderItem
from order.order_model_module import Order, OrderStatusEnum
from exceptions.exceptions_modules import ItemNotFoundError


@pytest.fixture
def customer():
    return Customer(
        name="Ahmad",
        email="ahmad@example.com",
        phone="0501234567"
    )


@pytest.fixture
def product():
    return Product(
        name="Mouse",
        description="Gaming Mouse",
        price=Decimal("150.00"),
        stock=15,
        category=ProductCategoryEnum.ELECTRONICS
    )


@pytest.fixture
def order_item(product):
    return OrderItem(
        product=product,
        quantity=2,
    )


# ==========================================
# Order creation
# ==========================================

def test_order_creation(customer):
    order = Order(customer=customer)

    assert order.customer is customer
    assert order.items == []
    assert order.created_date is not None


# ==========================================
# Customer relationship
# ==========================================

def test_order_customer_relationship(customer):
    order = Order(customer=customer)

    assert order.customer is customer


# ==========================================
# Add item
# ==========================================

def test_add_item(customer, order_item):
    order = Order(customer=customer)

    result = order.add_item(order_item)

    assert result is order_item
    assert order_item in order.items
    assert len(order.items) == 1


# ==========================================
# Remove item
# ==========================================

def test_remove_item(customer, order_item):
    order = Order(customer=customer)

    order.add_item(order_item)
    order.remove_item(order_item.order_item_id)

    assert order.items == []


def test_remove_missing_item(customer, order_item):
    order = Order(customer=customer)

    with pytest.raises(ItemNotFoundError):
        order.remove_item(order_item)


# ==========================================
# Subtotal
# ==========================================

def test_order_subtotal(customer, order_item):
    order = Order(customer=customer)

    order.add_item(order_item)

    assert order.calculate_subtotal() == Decimal("300.00")


# ==========================================
# Total
# ==========================================

def test_order_total(customer, order_item):
    order = Order(customer=customer)

    order.add_item(order_item)

    assert order.calculate_total() == Decimal("300.00")


# ==========================================
# Default status
# ==========================================

def test_order_default_status(customer):
    order = Order(customer=customer)

    assert order.status is OrderStatusEnum.PENDING

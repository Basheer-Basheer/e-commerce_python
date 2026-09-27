import pytest
from decimal import Decimal
from uuid import uuid4

from customer.customer_model import Customer
from product.product_model import Product, ProductCategoryEnum
from order.order_model_module import Order
from src.cart.cart_model import Cart
from repository.inmemoryrepository import InMemoryRepository
from services.order_service import OrderService
from services.checkout_service import CheckoutService
from src.repository.discount_protocol import NoDiscount, PercentageDiscount, FixedDiscount
from exceptions.exceptions_modules import ItemNotFoundError, ProductNotAddedToCartError, ProductNotAvailableError


@pytest.fixture
def order_repo():
    return InMemoryRepository[Order]()


@pytest.fixture
def customer_repo():
    return InMemoryRepository[Customer]()


@pytest.fixture
def product_repo():
    return InMemoryRepository[Product]()


@pytest.fixture
def order_service(order_repo, customer_repo, product_repo):
    return OrderService(order_repo, customer_repo, product_repo)


@pytest.fixture
def sample_customer(customer_repo):
    customer = Customer(name="Ali", email="ali@test.com", phone="0101234567")
    customer_repo.add(customer.customer_id, customer)
    return customer


@pytest.fixture
def sample_product(product_repo):
    product = Product(
        name="Mouse",
        description="Gaming mouse",
        price=Decimal("100.00"),
        stock=10,
        category=ProductCategoryEnum.ELECTRONICS,
    )
    product_repo.add(product.product_id, product)
    return product


@pytest.fixture
def cart_with_product(sample_product):
    cart = Cart()
    cart.add_product(sample_product, quantity=2)
    return cart


def test_successful_checkout_no_discount(order_service, sample_customer, cart_with_product):
    checkout_service = CheckoutService(order_service, discount=NoDiscount())
    order = checkout_service.checkout(sample_customer.customer_id, cart_with_product)

    assert order.customer == sample_customer
    assert len(order.items) == 1
    assert order.discount == Decimal("0.00")


def test_checkout_decreases_stock(order_service, sample_customer, cart_with_product, product_repo, sample_product):
    checkout_service = CheckoutService(order_service, discount=NoDiscount())
    checkout_service.checkout(sample_customer.customer_id, cart_with_product)

    updated_product = product_repo.get(sample_product.product_id)
    assert updated_product.stock == 8  # كان 10، طلبنا 2


def test_checkout_empty_cart_raises(order_service, sample_customer):
    checkout_service = CheckoutService(order_service, discount=NoDiscount())
    empty_cart = Cart()

    with pytest.raises(Exception):  # فكر: أي exception بالضبط متوقع هون؟
        checkout_service.checkout(sample_customer.customer_id, empty_cart)


def test_checkout_product_unavailable_raises(order_service, sample_customer, product_repo, sample_product):
    sample_product.discontinue()
    product_repo.update(sample_product.product_id, sample_product)

    cart = Cart()
    # لاحظ: add_product بالـCart نفسها ممكن أصلاً ترفض إضافة منتج discontinued
    with pytest.raises(ProductNotAddedToCartError):
        cart.add_product(sample_product, quantity=1)


def test_checkout_insufficient_stock_raises(order_service, sample_customer, sample_product):
    cart = Cart()
    with pytest.raises(Exception):
        cart.add_product(sample_product, quantity=999)  # أكبر من المخزون (10)


def test_checkout_percentage_discount(order_service, sample_customer, cart_with_product):
    checkout_service = CheckoutService(order_service, discount=PercentageDiscount(percentage=Decimal("10")))
    order = checkout_service.checkout(sample_customer.customer_id, cart_with_product)

    subtotal = order.calculate_subtotal()  # 100 * 2 = 200
    expected_discount = subtotal * Decimal("0.10")  # 20
    assert order.discount == expected_discount


def test_checkout_fixed_discount(order_service, sample_customer, cart_with_product):
    checkout_service = CheckoutService(order_service, discount=FixedDiscount(amount=Decimal("30.00")))
    order = checkout_service.checkout(sample_customer.customer_id, cart_with_product)

    assert order.discount == Decimal("30.00")


def test_checkout_final_total(order_service, sample_customer, cart_with_product):
    checkout_service = CheckoutService(order_service, discount=PercentageDiscount(percentage=Decimal("10")))
    order = checkout_service.checkout(sample_customer.customer_id, cart_with_product)

    subtotal = order.calculate_subtotal()  # 200
    final_total = subtotal - order.discount  # 200 - 20 = 180
    assert final_total == Decimal("180.00")
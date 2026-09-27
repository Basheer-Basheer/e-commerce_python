import pytest
from decimal import Decimal
from uuid import uuid4

from customer.customer_model import Customer
from product.product_model import Product, ProductCategoryEnum
from order.order_model_module import Order, OrderStatusEnum
from repository.inmemoryrepository import InMemoryRepository
from services.order_service import OrderService, ProductOrderRequest
from exceptions.exceptions_modules import (
    ItemNotFoundError,
    ProductNotAvailableError,
    OrderCantBeCancalledError,
    OrderCantBeConfirmedError,
)


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
def service(order_repo, customer_repo, product_repo):
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


def test_create_order_success(service, sample_customer, sample_product):
    order = service.create_order(
        sample_customer.customer_id,
        [{"product_id": sample_product.product_id, "quantity": 2}],
    )
    assert order.customer == sample_customer
    assert len(order.items) == 1
    assert order.items[0].quantity == 2


def test_create_order_decreases_stock(service, sample_customer, sample_product, product_repo):
    service.create_order(
        sample_customer.customer_id,
        [{"product_id": sample_product.product_id, "quantity": 3}],
    )
    updated_product = product_repo.get(sample_product.product_id)
    assert updated_product.stock == 7


def test_create_order_missing_customer_raises(service, sample_product):
    with pytest.raises(ItemNotFoundError):
        service.create_order(
            uuid4(),
            [{"product_id": sample_product.product_id, "quantity": 1}],
        )


def test_create_order_missing_product_raises(service, sample_customer):
    with pytest.raises(ItemNotFoundError):
        service.create_order(
            sample_customer.customer_id,
            [{"product_id": uuid4(), "quantity": 1}],
        )


def test_create_order_insufficient_stock_raises(service, sample_customer, sample_product):
    with pytest.raises(ProductNotAvailableError):
        service.create_order(
            sample_customer.customer_id,
            [{"product_id": sample_product.product_id, "quantity": 999}],
        )


def test_create_order_invalid_quantity_raises(service, sample_customer, sample_product):
    with pytest.raises(ProductNotAvailableError):
        service.create_order(
            sample_customer.customer_id,
            [{"product_id": sample_product.product_id, "quantity": 0}],
        )


def test_create_order_does_not_decrease_stock_if_any_item_fails(
    service, sample_customer, sample_product, product_repo
):
    second_product = Product(
        name="Keyboard",
        description="Mechanical keyboard",
        price=Decimal("50.00"),
        stock=1,
        category=ProductCategoryEnum.ELECTRONICS,
    )
    product_repo.add(second_product.product_id, second_product)

    with pytest.raises(ProductNotAvailableError):
        service.create_order(
            sample_customer.customer_id,
            [
                {"product_id": sample_product.product_id, "quantity": 2},
                {"product_id": second_product.product_id, "quantity": 999},
            ],
        )

    # تأكيد إنه المخزون ما نقص لأي منتج، لأنه العملية فشلت بالكامل
    assert product_repo.get(sample_product.product_id).stock == 10
    assert product_repo.get(second_product.product_id).stock == 1


def test_get_order(service, sample_customer, sample_product):
    order = service.create_order(
        sample_customer.customer_id,
        [{"product_id": sample_product.product_id, "quantity": 1}],
    )
    fetched = service.get_order(order.order_id)
    assert fetched == order


def test_get_missing_order_raises(service):
    with pytest.raises(ItemNotFoundError):
        service.get_order(uuid4())


def test_list_orders(service, sample_customer, sample_product):
    service.create_order(
        sample_customer.customer_id,
        [{"product_id": sample_product.product_id, "quantity": 1}],
    )
    orders = service.list_orders()
    assert len(orders) == 1


def test_add_item(service, sample_customer, sample_product, product_repo):
    order = service.create_order(
        sample_customer.customer_id,
        [{"product_id": sample_product.product_id, "quantity": 1}],
    )
    second_product = Product(
        name="Keyboard",
        description="Mechanical keyboard",
        price=Decimal("50.00"),
        stock=5,
        category=ProductCategoryEnum.ELECTRONICS,
    )
    product_repo.add(second_product.product_id, second_product)

    updated_order = service.add_item(order.order_id, second_product.product_id, 2)
    assert len(updated_order.items) == 2


def test_remove_item_restores_stock(service, sample_customer, sample_product, product_repo):
    order = service.create_order(
        sample_customer.customer_id,
        [{"product_id": sample_product.product_id, "quantity": 3}],
    )
    item_id = order.items[0].order_item_id

    service.remove_item(order.order_id, item_id)

    assert product_repo.get(sample_product.product_id).stock == 10


def test_cancel_order_pending(service, sample_customer, sample_product, product_repo):
    order = service.create_order(
        sample_customer.customer_id,
        [{"product_id": sample_product.product_id, "quantity": 4}],
    )
    service.cancel_order(order.order_id)

    updated_order = service.get_order(order.order_id)
    assert updated_order.status == OrderStatusEnum.CANCELLED
    assert product_repo.get(sample_product.product_id).stock == 10


def test_cancel_order_twice_raises(service, sample_customer, sample_product):
    order = service.create_order(
        sample_customer.customer_id,
        [{"product_id": sample_product.product_id, "quantity": 1}],
    )
    service.cancel_order(order.order_id)
    with pytest.raises(OrderCantBeCancalledError):
        service.cancel_order(order.order_id)


def test_cancel_completed_order_raises(service, sample_customer, sample_product, order_repo):
    order = service.create_order(
        sample_customer.customer_id,
        [{"product_id": sample_product.product_id, "quantity": 1}],
    )
    order.status = OrderStatusEnum.COMPLETED
    order_repo.update(order.order_id, order)

    with pytest.raises(OrderCantBeCancalledError):
        service.cancel_order(order.order_id)


def test_confirm_order_pending(service, sample_customer, sample_product):
    order = service.create_order(
        sample_customer.customer_id,
        [{"product_id": sample_product.product_id, "quantity": 1}],
    )
    service.confirm_order(order.order_id)

    updated_order = service.get_order(order.order_id)
    assert updated_order.status == OrderStatusEnum.CONFIRMED


def test_confirm_already_confirmed_order_raises(service, sample_customer, sample_product):
    order = service.create_order(
        sample_customer.customer_id,
        [{"product_id": sample_product.product_id, "quantity": 1}],
    )
    service.confirm_order(order.order_id)
    with pytest.raises(OrderCantBeConfirmedError):
        service.confirm_order(order.order_id)
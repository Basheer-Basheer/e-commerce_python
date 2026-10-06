
from decimal import Decimal

import pytest

from customer.customer_model import Customer
from order.order_model_module import Order, OrderStatusEnum
from order_item.order_item_module import OrderItem
from product.product_model import Product, ProductCategoryEnum
from repository.json_repository import JsonRepository
from repository.order_items_repository import OrderItemsRepository
from repository.order_repository import OrderRepository


@pytest.fixture
def product_repository(tmp_path):
    path = tmp_path / "products.json"
    path.write_text("{}")

    return JsonRepository(
        str(path),
        Product,
    )


@pytest.fixture
def customer_repository(tmp_path):
    path = tmp_path / "customers.json"
    path.write_text("{}")

    return JsonRepository(
        str(path),
        Customer,
    )


@pytest.fixture
def order_item_repository(
    tmp_path,
    product_repository,
):
    path = tmp_path / "order_items.json"
    path.write_text("{}")

    return OrderItemsRepository(
        str(path),
        product_repository,
    )


@pytest.fixture
def order_repository(
    tmp_path,
    customer_repository,
    order_item_repository,
):
    path = tmp_path / "orders.json"
    path.write_text("{}")

    return OrderRepository(
        str(path),
        customer_repository,
        order_item_repository,
    )


@pytest.fixture
def customer(customer_repository):
    customer = Customer(
        name="Basheer",
        email="basheer@test.com",
        phone="0500000000",
    )

    customer_repository.add(
        customer.get_id(),
        customer,
    )

    return customer


@pytest.fixture
def product(product_repository):
    product = Product(
        name="Laptop",
        description="Gaming Laptop",
        price=Decimal("1500.00"),
        stock=10,
        category=ProductCategoryEnum.ELECTRONICS,
    )

    product_repository.add(
        product.get_id(),
        product,
    )

    return product


@pytest.fixture
def order_item(
    product,
    order_item_repository,
):
    item = OrderItem(
        product=product,
        quantity=2,
    )

    order_item_repository.add(
        item.get_Id(),
        item,
    )

    return item


@pytest.fixture
def order(
    customer,
    order_item,
):
    return Order(
        customer=customer,
        items=[order_item],
    )


# ============================================================
# ADD
# ============================================================

def test_add_order(
    order_repository,
    order,
):
    result = order_repository.add(
        order.get_Id(),
        order,
    )

    assert result is order


# ============================================================
# GET
# ============================================================

def test_get_order(
    order_repository,
    order,
):
    order_repository.add(
        order.get_Id(),
        order,
    )

    result = order_repository.get(
        order.get_Id()
    )

    assert isinstance(result, Order)

    assert result.get_Id() == order.get_Id()
    assert result.customer.get_id() == order.customer.get_id()

    assert len(result.items) == 1
    assert result.items[0].get_Id() == order.items[0].get_Id()

    assert result.discount == order.discount
    assert result.status == order.status
    assert result.created_date == order.created_date


# ============================================================
# GET ALL
# ============================================================

def test_get_all_orders(
    order_repository,
    customer,
    order_item,
):
    order1 = Order(
        customer=customer,
        items=[order_item],
    )

    order2 = Order(
        customer=customer,
        items=[order_item],
    )

    order_repository.add(
        order1.get_Id(),
        order1,
    )

    order_repository.add(
        order2.get_Id(),
        order2,
    )

    result = order_repository.get_all()

    assert len(result) == 2
    assert all(isinstance(order, Order) for order in result)


# ============================================================
# UPDATE
# ============================================================

def test_update_order(
    order_repository,
    order,
):
    order_repository.add(
        order.get_Id(),
        order,
    )

    order.add_discount(Decimal("100.00"))

    result = order_repository.update(
        order.get_Id(),
        order,
    )

    assert result is order

    loaded = order_repository.get(
        order.get_Id()
    )

    assert loaded.discount == Decimal("100.00")


# ============================================================
# REMOVE
# ============================================================

def test_remove_order(
    order_repository,
    order,
):
    order_repository.add(
        order.get_Id(),
        order,
    )

    order_repository.remove(
        order.get_Id()
    )

    with pytest.raises(KeyError):
        order_repository.get(
            order.get_Id()
        )


# ============================================================
# MISSING FILE
# ============================================================

def test_missing_file_returns_empty_dict(
    tmp_path,
    customer_repository,
    order_item_repository,
):
    path = tmp_path / "missing.json"

    repository = OrderRepository(
        str(path),
        customer_repository,
        order_item_repository,
    )

    result = repository._load_data()

    assert result == {}


# ============================================================
# EMPTY FILE
# ============================================================

def test_empty_file_returns_empty_dict(
    tmp_path,
    customer_repository,
    order_item_repository,
):
    path = tmp_path / "empty.json"
    path.write_text("")

    repository = OrderRepository(
        str(path),
        customer_repository,
        order_item_repository,
    )

    result = repository._load_data()

    assert result == {}


# ============================================================
# INVALID JSON
# ============================================================

def test_invalid_json_raises_value_error(
    tmp_path,
    customer_repository,
    order_item_repository,
):
    path = tmp_path / "invalid.json"
    path.write_text("{ invalid json }")

    repository = OrderRepository(
        str(path),
        customer_repository,
        order_item_repository,
    )

    with pytest.raises(ValueError, match="Invalid JSON file"):
        repository.get_all()


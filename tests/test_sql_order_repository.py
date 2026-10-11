
import sqlite3
from decimal import Decimal
from uuid import uuid4

import pytest

from customer.customer_model import Customer, CustomerStatusEnum
from database.sql_order_repository import SqlOrderRepository
from order.order_model_module import Order, OrderStatusEnum
from order_item.order_item_module import OrderItem
from repository.order_repository import OrderRepository
from exceptions.exceptions_modules import NotMatchedObjects


class FakeCustomerRepository:
    def __init__(self):
        self.data = {}

    def add(self, obj_id, obj):
        self.data[obj_id] = obj
        return obj

    def get(self, obj_id):
        return self.data.get(obj_id)

    def get_all(self):
        return list(self.data.values())

    def update(self, obj_id, new_obj):
        self.data[obj_id] = new_obj
        return new_obj

    def remove(self, obj_id):
        self.data.pop(obj_id, None)


class FakeOrderItemRepository:
    def __init__(self):
        self.data = {}

    def add(self, obj_id, obj):
        self.data[obj_id] = obj
        return obj

    def get(self, obj_id):
        return self.data.get(obj_id)

    def get_all(self):
        return list(self.data.values())

    def update(self, obj_id, new_obj):
        self.data[obj_id] = new_obj
        return new_obj

    def remove(self, obj_id):
        self.data.pop(obj_id, None)


@pytest.fixture
def repository():
    connection = sqlite3.connect(":memory:")

    connection.execute("""
        CREATE TABLE orders (
            order_id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            discount TEXT NOT NULL,
            items_ids TEXT NOT NULL,
            status TEXT NOT NULL,
            created_date TEXT NOT NULL
        )
    """)

    customer_repository = FakeCustomerRepository()
    order_item_repository = FakeOrderItemRepository()

    repo = SqlOrderRepository(
        path=None,
        customer_repository=customer_repository,
        order_item_repository=order_item_repository,
        connection=connection,
        table_name="orders",
        id_column="order_id",
    )

    yield repo

    connection.close()


def make_customer():
    customer = Customer(
        name="Test Customer",
        email=f"{uuid4().hex[:8]}@example.com",
        phone="0501234567",
        status=CustomerStatusEnum.ACTIVE,
    )
    customer.customer_id = uuid4()
    return customer


def make_order_item():
    
    item = OrderItem.__new__(OrderItem)
    item.order_item_id = uuid4()
    return item


def make_order(repository, customer=None, items=None):
    customer = customer or make_customer()
    items = items if items is not None else [make_order_item()]

    repository.customer_repository.add(
        customer.customer_id, customer
    )

    for item in items:
        repository.order_item_repository.add(
            item.order_item_id, item
        )

    order = Order(customer=customer, items=items)
    return order


def test_add_order(repository):
    order = make_order(repository)

    result = repository.add(order.get_Id(), order)

    assert result is order

    row = repository.connection.execute(
        "SELECT order_id, customer_id, items_ids FROM orders "
        "WHERE order_id = ?",
        (str(order.get_Id()),),
    ).fetchone()

    assert row is not None
    assert row[0] == str(order.get_Id())
    assert row[1] == str(order.customer.customer_id)


def test_add_order_rejects_mismatched_id(repository):
    order = make_order(repository)

    with pytest.raises(NotMatchedObjects):
        repository.add(uuid4(), order)


def test_get_order(repository):
    order = make_order(repository)
    repository.add(order.get_Id(), order)

    result = repository.get(order.get_Id())

    assert result is not None
    assert isinstance(result, Order)
    assert result.get_Id() == order.get_Id()
    assert result.customer.customer_id == order.customer.customer_id
    assert len(result.items) == len(order.items)
    assert result.items[0].order_item_id == order.items[0].order_item_id


def test_get_missing_order(repository):
    result = repository.get(uuid4())

    assert result is None


def test_get_all_orders(repository):
    first = make_order(repository)
    second = make_order(repository)

    repository.add(first.get_Id(), first)
    repository.add(second.get_Id(), second)

    result = repository.get_all()

    assert len(result) == 2
    assert {order.get_Id() for order in result} == {
        first.get_Id(),
        second.get_Id(),
    }


def test_get_all_keeps_order_items_separate(repository):
    first = make_order(repository, items=[make_order_item()])
    second = make_order(
        repository,
        items=[make_order_item(), make_order_item()],
    )

    repository.add(first.get_Id(), first)
    repository.add(second.get_Id(), second)

    result = repository.get_all()

    orders_by_id = {order.get_Id(): order for order in result}

    assert len(orders_by_id[first.get_Id()].items) == 1
    assert len(orders_by_id[second.get_Id()].items) == 2


def test_update_order(repository):
    order = make_order(repository)
    repository.add(order.get_Id(), order)

    order.discount = Decimal("10.00")

    result = repository.update(order.get_Id(), order)

    assert result is order

    stored = repository.get(order.get_Id())

    assert stored is not None
    assert stored.discount == Decimal("10.00")
    assert stored.get_Id() == order.get_Id()


def test_update_rejects_mismatched_id(repository):
    order = make_order(repository)

    with pytest.raises(NotMatchedObjects):
        repository.update(uuid4(), order)


def test_remove_order(repository):
    order = make_order(repository)
    repository.add(order.get_Id(), order)

    repository.remove(order.get_Id())

    result = repository.get(order.get_Id())

    assert result is None


def test_remove_does_not_delete_another_order(repository):
    first = make_order(repository)
    second = make_order(repository)

    repository.add(first.get_Id(), first)
    repository.add(second.get_Id(), second)

    repository.remove(first.get_Id())

    assert repository.get(first.get_Id()) is None
    assert repository.get(second.get_Id()) is not None


import sqlite3
from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from product.product_model import (
    Product,
    ProductCategoryEnum,
    ProductStatusEnum,
)
from order_item.order_item_module import OrderItem
from database.sql_order_items_repository import SqlOrderItemsRepository
from exceptions.exceptions_modules import NotMatchedObjects


class FakeProductRepository:
    def __init__(self):
        self.products = {}

    def add(self, obj_id, obj):
        self.products[obj_id] = obj
        return obj

    def get(self, obj_id):
        return self.products.get(obj_id)


@pytest.fixture
def repository():
    connection = sqlite3.connect(":memory:")

    connection.execute(
        """
        CREATE TABLE order_items (
            order_item_id TEXT PRIMARY KEY,
            product_id TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price TEXT NOT NULL
        )
        """
    )

    product_repository = FakeProductRepository()

    repo = SqlOrderItemsRepository(
        connection=connection,
        product_repository=product_repository,
        table_name="order_items",
        id_column="order_item_id",
    )

    yield repo, product_repository

    connection.close()


@pytest.fixture
def product():
    return Product(
        "product-1",
        "Product description",
        Decimal("100.50"),
        10,
        ProductCategoryEnum.ELECTRONICS,
        ProductStatusEnum.ACTIVE,
    )


@pytest.fixture
def order_item(repository, product):
    repo, product_repository = repository

    product_repository.add(product.product_id, product)

    item = OrderItem(product=product, quantity=2)
    repo.add(item.get_Id(), item)

    return item


def test_add_and_get(repository, product):
    repo, product_repository = repository
    product_repository.add(product.product_id, product)

    item = OrderItem(product=product, quantity=3)

    result = repo.add(item.get_Id(), item)
    retrieved = repo.get(item.get_Id())

    assert result is item
    assert retrieved is not None
    assert retrieved.get_Id() == item.get_Id()
    assert retrieved.product.product_id == product.product_id
    assert retrieved.quantity == 3
    assert retrieved.unit_price == Decimal("100.50")


def test_get_returns_none_when_item_does_not_exist(repository):
    repo, _ = repository

    assert repo.get(uuid4()) is None


def test_get_all(repository, product):
    repo, product_repository = repository
    product_repository.add(product.product_id, product)

    first_item = OrderItem(product=product, quantity=2)
    second_item = OrderItem(product=product, quantity=4)

    repo.add(first_item.get_Id(), first_item)
    repo.add(second_item.get_Id(), second_item)

    result = repo.get_all()

    assert len(result) == 2
    assert {item.get_Id() for item in result} == {
        first_item.get_Id(),
        second_item.get_Id(),
    }


def test_get_all_returns_empty_list_when_table_is_empty(repository):
    repo, _ = repository

    assert repo.get_all() == []


def test_update(repository, product, order_item):
    repo, _ = repository

    updated_item = OrderItem(
        product=product,
        quantity=5,
    )
    updated_item.order_item_id = order_item.get_Id()

    result = repo.update(order_item.get_Id(), updated_item)
    retrieved = repo.get(order_item.get_Id())

    assert result is updated_item
    assert retrieved is not None
    assert retrieved.get_Id() == order_item.get_Id()
    assert retrieved.quantity == 5
    assert retrieved.unit_price == Decimal("100.50")


def test_add_raises_when_ids_do_not_match(repository, product):
    repo, product_repository = repository
    product_repository.add(product.product_id, product)

    item = OrderItem(product=product, quantity=1)

    with pytest.raises(NotMatchedObjects):
        repo.add(uuid4(), item)


def test_update_raises_when_ids_do_not_match(repository, product, order_item):
    repo, _ = repository

    updated_item = OrderItem(product=product, quantity=5)

    with pytest.raises(NotMatchedObjects):
        repo.update(order_item.get_Id(), updated_item)


def test_remove(repository, order_item):
    repo, _ = repository
    item_id = order_item.get_Id()

    repo.remove(item_id)

    assert repo.get(item_id) is None


def test_remove_does_not_fail_when_item_does_not_exist(repository):
    repo, _ = repository

    repo.remove(uuid4())

    assert repo.get_all() == []


import sqlite3
from decimal import Decimal
from uuid import uuid4

import pytest

from product.product_model import (
    Product,
    ProductCategoryEnum,
    ProductStatusEnum,
)
from database.sql_repository import SqlRepository


@pytest.fixture
def repository(tmp_path):
    db_path = tmp_path / "test.db"

    connection = sqlite3.connect(db_path)

    connection.execute("""
        CREATE TABLE products (
            product_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price TEXT NOT NULL,
            stock INTEGER NOT NULL,
            category TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)
    connection.commit()

    repo = SqlRepository(
        connection=connection,
        model=Product,
        table_name="products",
        id_column="product_id"
    )

    yield repo

    connection.close()


def make_product(name="Laptop"):
    product = Product(
        name=name,
        description="Test product",
        price=Decimal("2500.50"),
        stock=10,
        category=ProductCategoryEnum.ELECTRONICS,
        status=ProductStatusEnum.ACTIVE,
    )
    product.product_id = uuid4()

    return product


def test_add(repository):
    product = make_product()

    repository.add(product.get_id(), product)

    result = repository.connection.execute(
        f"SELECT * FROM products WHERE {repository.id_column} = ?",
        (str(product.get_id()),),
    ).fetchone()

    assert result is not None
    assert result[1] == product.name


def test_get(repository):
    product = make_product()
    repository.add(product.get_id(), product)

    result = repository.get(product.get_id())

    assert result is not None
    assert isinstance(result, Product)
    assert result.get_id() == product.get_id()
    assert result.name == product.name


def test_get_missing_product(repository):
    result = repository.get(uuid4())

    assert result is None


def test_get_all(repository):
    first = make_product("Laptop")
    second = make_product("Phone")

    repository.add(first.get_id(), first)
    repository.add(second.get_id(), second)

    result = repository.get_all()

    assert len(result) == 2
    assert all(isinstance(item, Product) for item in result)


def test_update(repository):
    product = make_product("Laptop")
    repository.add(product.get_id(), product)

    product.name = "Updated Laptop"
    product.stock = 20

    repository.update(product.get_id(), product)

    result = repository.connection.execute(
        f"SELECT name, stock FROM products WHERE {repository.id_column} = ?",
        (str(product.get_id()),),
    ).fetchone()

    assert result == ("Updated Laptop", 20)


def test_update_rejects_mismatched_id(repository):
    product = make_product()

    with pytest.raises(Exception):
        repository.update(uuid4(), product)


def test_remove(repository):
    product = make_product()
    repository.add(product.get_id(), product)

    repository.remove(product.get_id())

    result = repository.connection.execute(
        f"SELECT * FROM products WHERE {repository.id_column} = ?",
        (str(product.get_id()),),
    ).fetchone()

    assert result is None

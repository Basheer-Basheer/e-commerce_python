
import sqlite3
from uuid import uuid4

import pytest

from customer.customer_model import Customer, CustomerStatusEnum
from database.sql_repository import SqlRepository
from exceptions.exceptions_modules import NotMatchedObjects


@pytest.fixture
def repository(tmp_path):
    db_path = tmp_path / "test_customers.db"
    connection = sqlite3.connect(db_path)

    connection.execute("""
        CREATE TABLE customers (
            customer_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)
    connection.commit()

    repo = SqlRepository(
        connection=connection,
        model=Customer,
        table_name="customers",
        id_column="customer_id"
    )

    yield repo

    connection.close()


def make_customer(name="Test Customer"):
    customer = Customer(
        name=name,
        email=f"{uuid4().hex[:8]}@example.com",
        phone="0501234567",
        status=CustomerStatusEnum.ACTIVE,
    )
    customer.customer_id = uuid4()
    return customer


def test_add_customer(repository):
    customer = make_customer()

    repository.add(customer.get_id(), customer)

    result = repository.connection.execute(
        f"SELECT * FROM customers WHERE {repository.id_column} = ?",
        (str(customer.get_id()),),
    ).fetchone()

    assert result is not None
    assert result[1] == customer.name


def test_get_customer(repository):
    customer = make_customer()
    repository.add(customer.get_id(), customer)

    result = repository.get(customer.get_id())

    assert result is not None
    assert isinstance(result, Customer)
    assert result.get_id() == customer.get_id()
    assert result.name == customer.name
    assert result.email == customer.email


def test_get_missing_customer(repository):
    result = repository.get(uuid4())

    assert result is None


def test_get_all_customers(repository):
    first = make_customer("Customer One")
    second = make_customer("Customer Two")

    repository.add(first.get_id(), first)
    repository.add(second.get_id(), second)

    result = repository.get_all()

    assert len(result) == 2
    assert all(isinstance(item, Customer) for item in result)

    customer_ids = {item.get_id() for item in result}
    assert customer_ids == {first.get_id(), second.get_id()}


def test_update_customer(repository):
    customer = make_customer()
    repository.add(customer.get_id(), customer)

    customer.name = "Updated Customer"
    customer.email = "updated@example.com"

    repository.update(customer.get_id(), customer)

    result = repository.connection.execute(
        f"""
        SELECT name, email FROM customers
        WHERE {repository.id_column} = ?
        """,
        (str(customer.get_id()),),
    ).fetchone()

    assert result == ("Updated Customer", "updated@example.com")


def test_update_rejects_mismatched_id(repository):
    customer = make_customer()

    with pytest.raises(NotMatchedObjects):
        repository.update(uuid4(), customer)


def test_remove_customer(repository):
    customer = make_customer()
    repository.add(customer.get_id(), customer)

    repository.remove(customer.get_id())

    result = repository.connection.execute(
        f"SELECT * FROM customers WHERE {repository.id_column} = ?",
        (str(customer.get_id()),),
    ).fetchone()

    assert result is None

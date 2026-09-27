from uuid import UUID

import pytest
from typing import TypedDict


class CustomerData(TypedDict):
    name: str
    email: str
    phone: str


from customer.customer_model import Customer, CustomerStatusEnum


def test_customer_uuid_generation():
    customer = Customer(name="Basheer", email="basheer@example.com", phone="0501234567")

    assert isinstance(customer.customer_id, UUID)


def test_valid_customer():
    customer = Customer(name="Basheer", email="basheer@example.com", phone="0501234567")

    assert customer.name == "Basheer"
    assert customer.email == "basheer@example.com"
    assert customer.phone == "0501234567"


def test_customer_default_status():
    customer = Customer(name="Basheer", email="basheer@example.com", phone="0501234567")

    assert customer.status == CustomerStatusEnum.ACTIVE


def test_customer_status():
    customer = Customer(
        name="Basheer",
        email="basheer@example.com",
        phone="0501234567",
        status=CustomerStatusEnum.BLOCKED,
    )

    assert customer.status == CustomerStatusEnum.BLOCKED


@pytest.mark.parametrize("field", ["name", "email", "phone"])
def test_customer_empty_fields(field):
    data: CustomerData = {
        "name": "Basheer",
        "email": "basheer@example.com",
        "phone": "0501234567",
    }

    data[field] = ""

    with pytest.raises(ValueError):
        Customer(**data)

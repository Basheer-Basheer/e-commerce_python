
import json
from decimal import Decimal

import pytest

from customer.customer_model import Customer
from product.product_model import (
    Product,
    ProductCategoryEnum,
    ProductStatusEnum,
)
from repository.json_repository import JsonRepository


@pytest.fixture
def product():
    return Product(
        name="Laptop",
        description="Gaming Laptop",
        price=Decimal("1500.50"),
        stock=10,
        category=ProductCategoryEnum.ELECTRONICS,
    )


@pytest.fixture
def customer():
    return Customer(
        name="Basheer",
        email="basheer@test.com",
        phone="0500000000",
    )


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


# ============================================================
# ADD
# ============================================================

def test_add_product(product_repository, product):
    result = product_repository.add(
        product.get_id(),
        product,
    )

    assert result is product

    loaded = product_repository.get(product.get_id())

    assert loaded.product_id == product.product_id
    assert loaded.name == product.name
    assert loaded.price == product.price
    assert loaded.stock == product.stock


def test_add_customer(customer_repository, customer):
    result = customer_repository.add(
        customer.get_id(),
        customer,
    )

    assert result is customer

    loaded = customer_repository.get(customer.get_id())

    assert loaded.customer_id == customer.customer_id
    assert loaded.name == customer.name
    assert loaded.email == customer.email
    assert loaded.phone == customer.phone


# ============================================================
# GET
# ============================================================

def test_get_product(product_repository, product):
    product_repository.add(product.get_id(), product)

    result = product_repository.get(product.get_id())

    assert isinstance(result, Product)
    assert result.get_id() == product.get_id()
    assert result.name == product.name
    assert result.description == product.description
    assert result.price == product.price
    assert result.stock == product.stock
    assert result.category == product.category
    assert result.status == product.status


# ============================================================
# GET ALL
# ============================================================

def test_get_all_products(product_repository):
    product1 = Product(
        "Laptop",
        "Gaming Laptop",
        Decimal("1500"),
        10,
        ProductCategoryEnum.ELECTRONICS,
    )

    product2 = Product(
        "Mouse",
        "Gaming Mouse",
        Decimal("50"),
        20,
        ProductCategoryEnum.ELECTRONICS,
    )

    product_repository.add(product1.get_id(), product1)
    product_repository.add(product2.get_id(), product2)

    result = product_repository.get_all()

    assert len(result) == 2
    assert all(isinstance(product, Product) for product in result)


# ============================================================
# UPDATE
# ============================================================

def test_update_product(product_repository, product):
    product_repository.add(product.get_id(), product)

    product.price = Decimal("2000.00")
    product.stock = 5

    result = product_repository.update(
        product.get_id(),
        product,
    )

    assert result is product

    loaded = product_repository.get(product.get_id())

    assert loaded.price == Decimal("2000.00")
    assert loaded.stock == 5


# ============================================================
# REMOVE
# ============================================================

def test_remove_product(product_repository, product):
    product_repository.add(product.get_id(), product)

    product_repository.remove(product.get_id())

    with pytest.raises(KeyError):
        product_repository.get(product.get_id())


# ============================================================
# MISSING FILE
# ============================================================

def test_missing_file_returns_empty_dict(tmp_path):
    path = tmp_path / "missing.json"

    repository = JsonRepository(
        str(path),
        Product,
    )

    result = repository._load_data()

    assert result == {}


# ============================================================
# EMPTY FILE
# ============================================================

def test_empty_file_returns_empty_dict(tmp_path):
    path = tmp_path / "empty.json"

    path.write_text("")

    repository = JsonRepository(
        str(path),
        Product,
    )

    result = repository._load_data()

    assert result == {}


# ============================================================
# INVALID JSON
# ============================================================

def test_invalid_json_raises_value_error(tmp_path):
    path = tmp_path / "invalid.json"

    path.write_text("{ invalid json }")

    repository = JsonRepository(
        str(path),
        Product,
    )

    with pytest.raises(ValueError, match="Invalid JSON file"):
        repository.get_all()


# ============================================================
# JSON IS REALLY SAVED
# ============================================================

def test_product_is_saved_as_json(tmp_path, product):
    path = tmp_path / "products.json"
    path.write_text("{}")

    repository = JsonRepository(
        str(path),
        Product,
    )

    repository.add(product.get_id(), product)

    with open(path, "r") as file:
        data = json.load(file)

    assert str(product.get_id()) in data
    assert data[str(product.get_id())]["name"] == product.name
    assert data[str(product.get_id())]["price"] == str(product.price)


# ============================================================
# INVALID OBJECT DATA
# ============================================================

def test_invalid_product_data(tmp_path):
    path = tmp_path / "products.json"

    path.write_text(
        json.dumps(
            {
                "invalid-id": {
                    "product_id": "invalid-uuid",
                    "name": "Laptop",
                    "description": "Gaming",
                    "price": "1500.00",
                    "stock": 10,
                    "category": "ELECTRONICS",
                    "status": "ACTIVE",
                }
            }
        )
    )

    repository = JsonRepository(
        str(path),
        Product,
    )

    with pytest.raises(ValueError):
        repository.get_all()

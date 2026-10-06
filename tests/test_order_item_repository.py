
from decimal import Decimal

import pytest

from product.product_model import Product, ProductCategoryEnum
from repository.json_repository import JsonRepository
from repository.order_items_repository import OrderItemsRepository
from order_item.order_item_module import OrderItem


@pytest.fixture
def product_repository(tmp_path):
    path = tmp_path / "products.json"
    path.write_text("{}")

    return JsonRepository(
        str(path),
        Product,
    )


@pytest.fixture
def product(product_repository):
    product = Product(
        name="Laptop",
        description="Gaming Laptop",
        price=Decimal("1500.00"),
        stock=10,
        category=ProductCategoryEnum.ELECTRONICS,
    )

    product_repository.add(product.get_id(), product)

    return product


@pytest.fixture
def order_item_repository(tmp_path, product_repository):
    path = tmp_path / "order_items.json"
    path.write_text("{}")

    return OrderItemsRepository(
        str(path),
        product_repository,
    )


@pytest.fixture
def order_item(product):
    return OrderItem(
        product=product,
        quantity=2,
    )


# ============================================================
# ADD
# ============================================================

def test_add_order_item(order_item_repository, order_item):
    result = order_item_repository.add(
        order_item.get_Id(),
        order_item,
    )

    assert result is order_item


# ============================================================
# GET
# ============================================================

def test_get_order_item(order_item_repository, order_item):
    order_item_repository.add(
        order_item.get_Id(),
        order_item,
    )

    result = order_item_repository.get(
        order_item.get_Id()
    )

    assert isinstance(result, OrderItem)
    assert result.get_Id() == order_item.get_Id()
    assert result.product.get_id() == order_item.product.get_id()
    assert result.quantity == order_item.quantity
    assert result.unit_price == order_item.unit_price


# ============================================================
# GET ALL
# ============================================================

def test_get_all_order_items(
    order_item_repository,
    product,
):
    item1 = OrderItem(product, 2)
    item2 = OrderItem(product, 3)

    order_item_repository.add(item1.get_Id(), item1)
    order_item_repository.add(item2.get_Id(), item2)

    result = order_item_repository.get_all()

    assert len(result) == 2
    assert all(isinstance(item, OrderItem) for item in result)


# ============================================================
# UPDATE
# ============================================================

def test_update_order_item(
    order_item_repository,
    order_item,
):
    order_item_repository.add(
        order_item.get_Id(),
        order_item,
    )

    order_item.quantity = 5

    result = order_item_repository.update(
        order_item.get_Id(),
        order_item,
    )

    assert result is order_item

    loaded = order_item_repository.get(
        order_item.get_Id()
    )

    assert loaded.quantity == 5


# ============================================================
# REMOVE
# ============================================================

def test_remove_order_item(
    order_item_repository,
    order_item,
):
    order_item_repository.add(
        order_item.get_Id(),
        order_item,
    )

    order_item_repository.remove(
        order_item.get_Id()
    )

    with pytest.raises(KeyError):
        order_item_repository.get(
            order_item.get_Id()
        )


# ============================================================
# MISSING FILE
# ============================================================

def test_missing_file_returns_empty_dict(
    tmp_path,
    product_repository,
):
    path = tmp_path / "missing.json"

    repository = OrderItemsRepository(
        str(path),
        product_repository,
    )

    result = repository._load_data()

    assert result == {}


# ============================================================
# EMPTY FILE
# ============================================================

def test_empty_file_returns_empty_dict(
    tmp_path,
    product_repository,
):
    path = tmp_path / "empty.json"
    path.write_text("")

    repository = OrderItemsRepository(
        str(path),
        product_repository,
    )

    result = repository._load_data()

    assert result == {}


# ============================================================
# INVALID JSON
# ============================================================

def test_invalid_json_raises_value_error(
    tmp_path,
    product_repository,
):
    path = tmp_path / "invalid.json"
    path.write_text("{ invalid json }")

    repository = OrderItemsRepository(
        str(path),
        product_repository,
    )

    with pytest.raises(ValueError, match="Invalid JSON file"):
        repository.get_all()


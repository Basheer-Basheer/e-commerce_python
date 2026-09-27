import pytest
from uuid import UUID

from exceptions.exceptions_modules import InsufficientStockAmount
from product.product_model import Product, ProductCategoryEnum, ProductStatusEnum
from decimal import Decimal


@pytest.fixture
def product():
    return Product(
        name="Laptop",
        description="Gaming Laptop",
        price=Decimal("3000.00"),
        category=ProductCategoryEnum.ELECTRONICS,
        stock=10,
    )


def test_define_new_product_success():
    product = Product(
        name="Mouse",
        description="New mouse 2026",
        price=150,
        stock=0,
        category=ProductCategoryEnum.ELECTRONICS,
        status=ProductStatusEnum.ACTIVE
    )

    assert isinstance(product.product_id, UUID) is True
    assert product.name == "Mouse"
    assert product.description == "New mouse 2026"
    assert product.price == 150
    assert product.stock == 0
    assert product.category == ProductCategoryEnum.ELECTRONICS
    assert product.status == ProductStatusEnum.ACTIVE


def test_define_new_product_name_fail():
    with pytest.raises(ValueError):
        product = Product(
            name="",
            description="New mouse 2026",
            price=150,
            stock=0,
            category=ProductCategoryEnum.ELECTRONICS,
            status=ProductStatusEnum.ACTIVE
        )


def test_define_new_product_success_default_status():
    product = Product(
        name="Mouse",
        description="New mouse 2026",
        price=150,
        stock=0,
        category=ProductCategoryEnum.ELECTRONICS, )

    assert isinstance(product.product_id, UUID) is True

    assert product.name == "Mouse"
    assert product.description == "New mouse 2026"
    assert product.price == 150
    assert product.stock == 0
    assert product.category == ProductCategoryEnum.ELECTRONICS
    assert product.status == ProductStatusEnum.ACTIVE


def test_define_new_product_price_fail():
    with pytest.raises(ValueError):
        product = Product(
            name="Mouse",
            description="New mouse 2026",
            price=0,
            stock=0,
            category=ProductCategoryEnum.ELECTRONICS,
            status=ProductStatusEnum.ACTIVE
        )
    with pytest.raises(ValueError):
        product = Product(
            name="Mouse",
            description="New mouse 2026",
            price=-20,
            stock=0,
            category=ProductCategoryEnum.ELECTRONICS,
            status=ProductStatusEnum.ACTIVE
        )


def test_define_new_product_stock_fail():
    with pytest.raises(ValueError):
        product = Product(
            name="Mouse",
            description="New mouse 2026",
            price=150,
            stock=-20,
            category=ProductCategoryEnum.ELECTRONICS,
            status=ProductStatusEnum.ACTIVE
        )


def test_define_new_product_name_fail_type_error():
    with pytest.raises(TypeError):
        product = Product(
            name=15,
            description="New mouse 2026",
            price=150,
            stock=20,
            category=ProductCategoryEnum.ELECTRONICS,
            status=ProductStatusEnum.ACTIVE
        )


def test_first_decimal_():
    product = Product(
        name="Mouse",
        description="New mouse 2026",
        price=150.1,
        stock=0,
        category=ProductCategoryEnum.ELECTRONICS,
        status=ProductStatusEnum.ACTIVE
    )

    assert product.price == Decimal("150.10")


def test_first_decimal_2():
    product = Product(
        name="Mouse",
        description="New mouse 2026",
        price="150.1",
        stock=0,
        category=ProductCategoryEnum.ELECTRONICS,
        status=ProductStatusEnum.ACTIVE
    )

    assert product.price == Decimal("150.10")


def test_first_decimal_3():
    product = Product(
        name="Mouse",
        description="New mouse 2026",
        price="150.126",
        stock=0,
        category=ProductCategoryEnum.ELECTRONICS,
        status=ProductStatusEnum.ACTIVE
    )

    assert product.price == Decimal("150.13")


def test_first_decimal_4():
    product = Product(
        name="Mouse",
        description="New mouse 2026",
        price="150.042",
        stock=0,
        category=ProductCategoryEnum.ELECTRONICS,
        status=ProductStatusEnum.ACTIVE
    )

    assert product.price == Decimal("150.04")


def test_first_decimal_fail():
    with pytest.raises(ValueError):
        product = Product(
            name="Mouse",
            description="New mouse 2026",
            price="hello",
            stock=0,
            category=ProductCategoryEnum.ELECTRONICS,
            status=ProductStatusEnum.ACTIVE
        )


# ==================================================
# PRODUCT STATUS
# ==================================================


def test_activate_product(product):
    product.deactivate()

    product.activate()

    assert product.status is ProductStatusEnum.ACTIVE


def test_activate_already_active_product(product):
    with pytest.raises(ValueError, match="already active"):
        product.activate()


def test_deactivate_product(product):
    product.deactivate()

    assert product.status is ProductStatusEnum.INACTIVE


def test_deactivate_already_inactive_product(product):
    product.deactivate()

    with pytest.raises(ValueError, match="already inactive"):
        product.deactivate()


def test_discontinue_product(product):
    product.discontinue()

    assert product.status is ProductStatusEnum.DISCONTINUED


def test_discontinue_already_discontinued_product(product):
    product.discontinue()

    with pytest.raises(ValueError, match="already discontinued"):
        product.discontinue()


def test_discontinued_can_become_active(product):
    product.discontinue()

    product.activate()

    assert product.status is ProductStatusEnum.ACTIVE


def test_discontinued_can_become_inactive(product):
    product.discontinue()

    product.deactivate()

    assert product.status is ProductStatusEnum.INACTIVE


def test_inactive_can_become_discontinued(product):
    product.deactivate()

    product.discontinue()

    assert product.status is ProductStatusEnum.DISCONTINUED


# ==================================================
# INCREASE STOCK
# ==================================================


def test_increase_stock(product):
    product.increase_stock(5)

    assert product.stock == 15


def test_increase_stock_by_zero(product):
    with pytest.raises(ValueError, match="more than zero"):
        product.increase_stock(0)


def test_increase_stock_by_negative_amount(product):
    with pytest.raises(ValueError, match="more than zero"):
        product.increase_stock(-5)


def test_increase_stock_requires_integer(product):
    with pytest.raises(TypeError, match="int"):
        product.increase_stock(2.5)


def test_increase_stock_rejects_string(product):
    with pytest.raises(TypeError, match="int"):
        product.increase_stock("5")


# ==================================================
# DECREASE STOCK
# ==================================================


def test_decrease_stock(product):
    product.decrease_stock(3)

    assert product.stock == 7


def test_decrease_entire_stock(product):
    product.decrease_stock(10)

    assert product.stock == 0


def test_decrease_stock_by_zero(product):
    with pytest.raises(ValueError, match="more than zero"):
        product.decrease_stock(0)


def test_decrease_stock_by_negative_amount(product):
    with pytest.raises(ValueError, match="more than zero"):
        product.decrease_stock(-5)


def test_decrease_stock_requires_integer(product):
    with pytest.raises(TypeError, match="int"):
        product.decrease_stock(2.5)


def test_decrease_stock_rejects_string(product):
    with pytest.raises(TypeError, match="int"):
        product.decrease_stock("5")


def test_decrease_stock_when_insufficient(product):
    with pytest.raises(InsufficientStockAmount):
        product.decrease_stock(11)


def test_stock_does_not_change_after_failed_decrease(product):
    original_stock = product.stock

    with pytest.raises(InsufficientStockAmount):
        product.decrease_stock(20)

    assert product.stock == original_stock

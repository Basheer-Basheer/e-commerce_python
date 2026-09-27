import pytest
from decimal import Decimal

from cart.cart_model import Cart
from exceptions.exceptions_modules import (
    ProductAddToCartError,
    ProductNotAddedToCartError,
    ProductNotFoundError,
)
from product.product_model import (
    Product,
    ProductCategoryEnum,
    ProductStatusEnum,
)


@pytest.fixture
def product():
    return Product(
        name="Laptop",
        description="Test Laptop",
        price=Decimal("100.00"),
        stock=10,
        category=ProductCategoryEnum.ELECTRONICS,
    )


@pytest.fixture
def second_product():
    return Product(
        name="Mouse",
        description="Test Mouse",
        price=Decimal("50.00"),
        stock=5,
        category=ProductCategoryEnum.ELECTRONICS,
    )


@pytest.fixture
def cart():
    return Cart()


# =========================
# is_empty
# =========================

def test_cart_is_empty_when_created(cart):
    assert cart.is_empty() is True


def test_cart_is_not_empty_after_adding_product(cart, product):
    cart.add_product(product, 2)

    assert cart.is_empty() is False


def test_cart_is_empty_after_clear(cart, product):
    cart.add_product(product, 2)
    cart.clear()

    assert cart.is_empty() is True


# =========================
# add_product
# =========================

def test_add_product(cart, product):
    result = cart.add_product(product, 2)

    assert result is None
    assert len(cart.items) == 1
    assert cart.items[0]["product_id"] == str(product.product_id)
    assert cart.items[0]["product_price"] == Decimal("100.00")
    assert cart.items[0]["product_quantity"] == 2


def test_add_multiple_products(cart, product, second_product):
    cart.add_product(product, 2)
    cart.add_product(second_product, 3)

    assert len(cart.items) == 2



def test_add_product_with_quantity_greater_than_stock(
    cart,
    product,
):
    with pytest.raises(ProductNotAddedToCartError):
        cart.add_product(product, 11)

    assert cart.is_empty() is True


def test_add_inactive_product_raises_error(cart, product):
    product.deactivate()

    with pytest.raises(ProductNotAddedToCartError):
        cart.add_product(product, 2)

    assert cart.is_empty() is True


def test_add_discontinued_product_raises_error(cart, product):
    product.discontinue()

    with pytest.raises(ProductNotAddedToCartError):
        cart.add_product(product, 2)

    assert cart.is_empty() is True


def test_add_product_with_zero_quantity_raises_error(cart, product):
    with pytest.raises(ProductNotAddedToCartError):
        cart.add_product(product, 0)

    assert cart.is_empty() is True


def test_add_product_with_negative_quantity_raises_error(cart, product):
    with pytest.raises(ProductNotAddedToCartError):
        cart.add_product(product, -1)

    assert cart.is_empty() is True


# =========================
# remove_product
# =========================

def test_remove_product(cart, product):
    cart.add_product(product, 2)

    cart.remove_product(str(product.product_id))

    assert cart.is_empty() is True


def test_remove_product_keeps_other_products(
    cart,
    product,
    second_product,
):
    cart.add_product(product, 2)
    cart.add_product(second_product, 3)

    cart.remove_product(str(product.product_id))

    assert len(cart.items) == 1
    assert cart.items[0]["product_id"] == str(second_product.product_id)


def test_remove_non_existing_product_raises_error(cart):
    with pytest.raises(ProductNotFoundError):
        cart.remove_product("does-not-exist")


def test_remove_product_with_non_string_id_raises_type_error(
    cart,
):
    with pytest.raises(TypeError):
        cart.remove_product(123)


# =========================
# update_quantity
# =========================

def test_update_quantity(cart, product):
    cart.add_product(product, 2)

    cart.update_quantity(str(product.product_id), 5)

    assert cart.items[0]["product_quantity"] == 5


def test_update_quantity_to_zero_raises_error(cart, product):
    cart.add_product(product, 2)

    with pytest.raises(ValueError):
        cart.update_quantity(str(product.product_id), 0)

    assert cart.items[0]["product_quantity"] == 2


def test_update_quantity_to_negative_raises_error(cart, product):
    cart.add_product(product, 2)

    with pytest.raises(ValueError):
        cart.update_quantity(str(product.product_id), -1)

    assert cart.items[0]["product_quantity"] == 2


def test_update_quantity_with_non_integer_raises_error(
    cart,
    product,
):
    cart.add_product(product, 2)

    with pytest.raises(TypeError):
        cart.update_quantity(str(product.product_id), "5")


def test_update_quantity_for_non_existing_product_raises_error(
    cart,
):
    with pytest.raises(ProductNotFoundError):
        cart.update_quantity("does-not-exist", 5)


def test_update_quantity_with_non_string_product_id_raises_error(
    cart,
    product,
):
    cart.add_product(product, 2)

    with pytest.raises(TypeError):
        cart.update_quantity(123, 5)


# =========================
# clear
# =========================

def test_clear_cart(cart, product, second_product):
    cart.add_product(product, 2)
    cart.add_product(second_product, 1)

    cart.clear()

    assert cart.items == []
    assert cart.is_empty() is True


def test_clear_empty_cart(cart):
    cart.clear()

    assert cart.items == []
    assert cart.is_empty() is True


# =========================
# calculate_subtotal
# =========================

def test_calculate_subtotal(cart, product):
    cart.add_product(product, 2)

    assert cart.calculate_subtotal() == Decimal("200.00")


def test_calculate_subtotal_with_multiple_products(
    cart,
    product,
    second_product,
):
    cart.add_product(product, 2)
    cart.add_product(second_product, 3)

    assert cart.calculate_subtotal() == Decimal("350.00")


def test_calculate_subtotal_empty_cart(cart):
    assert cart.calculate_subtotal() == Decimal("0.00")


def test_calculate_subtotal_after_update_quantity(cart, product):
    cart.add_product(product, 2)

    cart.update_quantity(str(product.product_id), 5)

    assert cart.calculate_subtotal() == Decimal("500.00")


def test_calculate_subtotal_after_remove_product(
    cart,
    product,
    second_product,
):
    cart.add_product(product, 2)
    cart.add_product(second_product, 3)

    cart.remove_product(str(product.product_id))

    assert cart.calculate_subtotal() == Decimal("150.00")


# =========================
# Cart isolation
# =========================

def test_each_cart_has_its_own_items(product):
    cart1 = Cart()
    cart2 = Cart()

    cart1.add_product(product, 2)

    assert len(cart1.items) == 1
    assert len(cart2.items) == 0
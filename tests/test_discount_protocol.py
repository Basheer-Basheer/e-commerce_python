import pytest
from decimal import Decimal

from src.repository.discount_protocol import NoDiscount, PercentageDiscount, FixedDiscount


def test_no_discount():
    discount = NoDiscount()
    result = discount.calculate_discount(Decimal("100.00"))
    assert result == Decimal("0.00")


def test_percentage_discount():
    discount = PercentageDiscount(percentage=Decimal("10"))
    result = discount.calculate_discount(Decimal("100.00"))
    assert result == Decimal("10.00")


def test_percentage_discount_different_value():
    discount = PercentageDiscount(percentage=Decimal("25"))
    result = discount.calculate_discount(Decimal("200.00"))
    assert result == Decimal("50.00")


def test_fixed_discount():
    discount = FixedDiscount(amount=Decimal("20.00"))
    result = discount.calculate_discount(Decimal("100.00"))
    assert result == Decimal("20.00")


def test_invalid_percentage_negative():
    with pytest.raises(ValueError):
        PercentageDiscount(percentage=Decimal("-10"))


def test_invalid_percentage_over_100():
    with pytest.raises(ValueError):
        PercentageDiscount(percentage=Decimal("150"))


def test_invalid_fixed_discount_negative():
    with pytest.raises(ValueError):
        FixedDiscount(amount=Decimal("-5"))


def test_invalid_fixed_discount_zero():
    with pytest.raises(ValueError):
        FixedDiscount(amount=Decimal("0"))


def test_fixed_discount_cannot_exceed_order_total():
    discount = FixedDiscount(amount=Decimal("100.00"))
    result = discount.calculate_discount(Decimal("50.00"))
    assert result == Decimal("50.00")   # الخصم محدود عند الـsubtotal، مش 100
from typing import Protocol
from decimal import Decimal


class DiscountStrategy(Protocol):
    def calculate_discount(self, subtotal: Decimal) -> Decimal:
        ...


class NoDiscount:
    def calculate_discount(self, subtotal: Decimal) -> Decimal:
        return Decimal("0.00")


class PercentageDiscount:
    def __init__(self, percentage: Decimal) -> None:
        if 1 < percentage <= 100:
            self.percentage = percentage
        else :
            raise ValueError("Percentage should be between 0 and 100")
    def calculate_discount(self, subtotal: Decimal) -> Decimal:
        return subtotal * (self.percentage / Decimal("100"))


class FixedDiscount:
    def __init__(self, amount: Decimal) -> None:
        if amount > 0 :
            self.amount = amount
        else :
            raise ValueError("Amount should be a valid number")

    def calculate_discount(self, subtotal: Decimal) -> Decimal:
        return min(self.amount, subtotal)
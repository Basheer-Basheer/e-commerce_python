from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from math import prod
from uuid import UUID, uuid4
from product.product_model import Product


@dataclass
class OrderItem:
    product: Product
    quantity: int
    unit_price: Decimal = field(init=False)
    order_item_id: UUID = field(init=False, default_factory=uuid4)

    def __post_init__(self):

        if not isinstance(self.product, Product):
            raise TypeError("Product must be an instance of Product")
        if not isinstance(self.quantity, int):
            raise TypeError("Quantity must be integer")

        if self.quantity <= 0:
            raise ValueError("Quantity must be greater than zero")

        self.unit_price = self.product.price

    def subtotal(self) -> Decimal:
        return (self.unit_price * self.quantity).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )


    


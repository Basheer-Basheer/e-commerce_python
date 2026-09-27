from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from typing import TypedDict
from uuid import UUID


from exceptions.exceptions_modules import (
    ProductAddToCartError,
    ProductNotAddedToCartError,
    ProductNotFoundError,
)
from product.product_model import Product


class CartItemsType(TypedDict):
    product_id: UUID
    product_price: Decimal
    product_quantity: int


@dataclass
class Cart:
    items: list[CartItemsType] = field(init=False, default_factory=list)

    def add_product(self, product: Product, quantity: int) -> None:
        for index, item in enumerate(self.items):
            if item["product_id"] == product.product_id:
                self.items[index]["product_quantity"] += quantity
                return

        if product.is_available(quantity):
            self.items.append(
                {
                    "product_id": product.product_id,
                    "product_price": product.price,
                    "product_quantity": quantity,
                }
            )
            return
        raise ProductNotAddedToCartError("Product has not been added to cart")

    def remove_product(self, product_id: UUID) -> None:
        if not isinstance(product_id, UUID):
            raise TypeError("please insert string id")

        for index, item in enumerate(self.items):
            if item["product_id"] == product_id:
                del self.items[index]
                return

        raise ProductNotFoundError("Product does not exist in the cart")

    def update_quantity(self, product_id: str, new_quantity: int) -> None:
        if not isinstance(product_id, str):
            raise TypeError("please insert string id")

        if not isinstance(new_quantity, int):
            raise TypeError("please insert int quantity")

        if new_quantity <= 0:
            raise ValueError("please insert positive quantity")

        for index, item in enumerate(self.items):
            if item["product_id"] == product_id:
                self.items[index]["product_quantity"] = new_quantity
                return

        raise ProductNotFoundError("Product does not exist in the cart")

    def clear(self) -> None:
        self.items = []

    def calculate_subtotal(self) -> Decimal:
        sub_total = Decimal("0.00")

        for item in self.items:
            sub_total += (item["product_price"] * item["product_quantity"]).quantize(
                Decimal("0.00"), rounding=ROUND_HALF_UP
            )

        return sub_total

    def is_empty(
        self,
    ) -> bool:
        return not self.items

from turtle import update
from uuid import UUID

from cart.cart_model import Cart
from order.order_model_module import Order
from repository.discount_protocol import DiscountStrategy
from services.order_service import OrderService
from tests.test_order_module import customer


class CheckoutService:
    def __init__(self, order_service: OrderService, discount: DiscountStrategy):
        self.order_service = order_service
        self.discount = discount

    def checkout(
        self,
        customer_id: UUID,
        cart: Cart,
    ) -> Order:
        items = []
        if len(cart.items) <= 0:
            raise ValueError("Cart should not be empty")
        for item in cart.items:
            items.append(
                {
                    "product_id": item.get("product_id"),
                    "quantity": item.get("product_quantity"),
                }
            )
        order = self.order_service.create_order(customer_id=customer_id, items=items)
        discount = self.discount.calculate_discount(order.calculate_subtotal())
        updated_order = self.order_service.apply_discount(order.order_id, discount)
        return updated_order

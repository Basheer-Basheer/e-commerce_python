from decimal import Decimal
from uuid import UUID
from customer.customer_model import Customer
from order.order_model_module import Order, OrderStatusEnum
from exceptions.exceptions_modules import (
    OrderCantBeCancalledError,
    OrderCantBeConfirmedError,
    ProductNotAvailableError,
)
from order_item.order_item_module import OrderItem
from product.product_model import Product
from repository.repository_protocol import RepositoryProtocol
from typing import TypedDict


class ProductOrderRequest(TypedDict):
    product_id: UUID
    quantity: int


class OrderService:
    def __init__(
        self,
        order_repository: RepositoryProtocol[Order],
        customer_repository: RepositoryProtocol[Customer],
        product_repository: RepositoryProtocol[Product],
    ) -> None:
        self.order_repository = order_repository
        self.customer_repository = customer_repository
        self.product_repository = product_repository

    def create_order(
        self, customer_id: UUID, items: list[ProductOrderRequest]
    ) -> Order:
        customer = self.customer_repository.get(customer_id)
        products: list[tuple[Product, int]] = []
        order_items: list[OrderItem] = []

        for item in items:
            product = self.product_repository.get(item["product_id"])

            if not product.is_available(item["quantity"]):
                raise ProductNotAvailableError(
                    f"Product {product.name} is not available in the requested quantity"
                )

            order_items.append(OrderItem(product=product, quantity=item["quantity"]))

        for order_item in order_items:
            order_item.product.decrease_stock(order_item.quantity)
            self.product_repository.update(
                order_item.product.product_id, order_item.product
            )

        order = Order(
            customer=customer,
            items=order_items,
        )
        self.order_repository.add(order.order_id, order)

        return order

    def get_order(self, order_id: UUID) -> Order:
        order = self.order_repository.get(order_id)
        return order

    def list_orders(self) -> list[Order]:
        return self.order_repository.get_all()

    def add_item(self, order_id: UUID, new_item_id: UUID, quantity: int) -> Order:
        order = self.order_repository.get(order_id)

        new_product = self.product_repository.get(new_item_id)

        order.add_item(
            OrderItem(
                product=new_product,
                quantity=quantity,
            )
        )
        self.order_repository.update(order.order_id, order)
        return order

    def remove_item(self, order_id: UUID, item_id: UUID) -> Order:
        order = self.order_repository.get(order_id)
        removed_item = order.remove_item(item_id)  # بحث واحد بس، جوه الـmodel

        removed_item.product.increase_stock(removed_item.quantity)
        self.product_repository.update(
            removed_item.product.product_id, removed_item.product
        )

        self.order_repository.update(order.order_id, order)
        return order

    def cancel_order(self, order_id: UUID) -> None:

        order = self.order_repository.get(order_id)

        if order.status in (OrderStatusEnum.PENDING, OrderStatusEnum.CONFIRMED):
            order.status = OrderStatusEnum.CANCELLED
            for order_item in order.items:
                order_item.product.increase_stock(order_item.quantity)
                self.product_repository.update(
                    order_item.product.product_id, order_item.product
                )
            self.order_repository.update(order.order_id, order)
        else:
            raise OrderCantBeCancalledError("Order can not be cancalled .. ")

    def confirm_order(self, order_id: UUID) -> None:
        order = self.order_repository.get(order_id)
        if order.status is OrderStatusEnum.PENDING:
            order.status = OrderStatusEnum.CONFIRMED
            self.order_repository.update(order.order_id, order)
        else:
            raise OrderCantBeConfirmedError("Order Cannot be confirmed...")


    def apply_discount(self,order_id:UUID, amount:Decimal) -> Order:
        order = self.get_order(order_id=order_id)
        order.add_discount(amount=amount)
        self.order_repository.update(order_id, order)
        return order
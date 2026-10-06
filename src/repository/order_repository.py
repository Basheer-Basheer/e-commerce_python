
from decimal import Decimal
from typing import Protocol, Self, Generic, TypeVar
from uuid import UUID
import json

from customer.customer_model import Customer
from exceptions.exceptions_modules import NotMatchedObjects
from order.order_model_module import Order, OrderStatusEnum
from order_item.order_item_module import OrderItem
from repository.repository_protocol import RepositoryProtocol


class OrderRepository:
    def __init__(
        self,
        path,
        customer_repository: RepositoryProtocol,
        order_item_repository: RepositoryProtocol,
    ):
        self.path = path
        self.customer_repository = customer_repository
        self.order_item_repository = order_item_repository

    def _load_data(self):
        try:
            with open(self.path, "r") as file:
                content = file.read()

            if not content.strip():
                return {}

            return json.loads(content)

        except FileNotFoundError:
            return {}

        except json.JSONDecodeError:
            raise ValueError("Invalid JSON file")

    def add(self, obj_id: UUID, obj: Order) -> Order:
        if not (obj.get_Id() == obj_id):
            raise NotMatchedObjects("Ids are not matching ... ")

        data = self._load_data()

        new_dict = obj.to_dict()
        data[str(obj_id)] = new_dict

        with open(self.path, "w") as file:
            json.dump(data, file)

        return obj

    def get(self, obj_id: UUID) -> Order:
        data = self._load_data()

        order = data[str(obj_id)]

        customer = self.customer_repository.get(
            UUID(order["customer_id"])
        )

        items = []
        for i in order["items_ids"]:
            item = self.order_item_repository.get(UUID(str(i)))
            items.append(item)

        return self._from_dict(order, customer, items)

    def _from_dict(
        self,
        data: dict,
        customer: Customer,
        items: list[OrderItem],
    ) -> Order:

        order = Order(
            customer=customer,
            items=items,
        )

        order.order_id = UUID(data["order_id"])
        order.discount = Decimal(data["discount"])
        order.status = OrderStatusEnum[data["status"]]
        order.created_date = data["created_date"]

        return order

    def get_all(self) -> list[Order]:
        all_orders = []

        data = self._load_data()

        for order in data.values():
            customer = self.customer_repository.get(
                UUID(order["customer_id"])
            )

            items = []

            for i in order["items_ids"]:
                item = self.order_item_repository.get(UUID(str(i)))
                items.append(item)

            all_orders.append(
                self._from_dict(order, customer, items)
            )

        return all_orders

    def update(self, obj_id: UUID, new_obj: Order) -> Order:
        data = self._load_data()

        if not (new_obj.get_Id() == obj_id):
            raise NotMatchedObjects("Objects are not matched ... ")

        data[str(obj_id)] = new_obj.to_dict()

        with open(self.path, "w") as file:
            json.dump(data, file)

        return new_obj

    def remove(self, obj_id: UUID) -> None:
        data = self._load_data()

        del data[str(obj_id)]

        with open(self.path, "w") as file:
            json.dump(data, file)


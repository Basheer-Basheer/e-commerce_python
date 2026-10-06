from decimal import Decimal
from math import e
from uuid import UUID
import json
from customer.customer_model import Customer
from exceptions.exceptions_modules import NotMatchedObjects
from order.order_model_module import Order, OrderStatusEnum
from order_item.order_item_module import OrderItem
from repository.repository_protocol import RepositoryProtocol


class OrderItemsRepository:
    def __init__(
        self,
        path,
        product_repository: RepositoryProtocol,
    ):
        self.path = path
        self.product_repository = product_repository

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

    def add(self, obj_id: UUID, obj: OrderItem) -> OrderItem | dict:
        if not (obj.get_Id() == obj_id):
            raise NotMatchedObjects("Ids are not matching ... ")

        data = self._load_data()

        new_dict = obj.to_dict()
        data[str(obj_id)] = new_dict

        with open(self.path, "w") as file:
            json.dump(data, file)

        return obj

    def get(self, obj_id: UUID) -> OrderItem | dict:
        data = self._load_data()

        order_item = data[str(obj_id)]

        product = self.product_repository.get(UUID(order_item["product_id"]))

        return self._from_dict(order_item, product)

    def _from_dict(self, data: dict, product) -> OrderItem:
        orderItem = OrderItem(
            product=product,
            quantity=data["quantity"]
        )
        orderItem.unit_price = Decimal(data["unit_price"])
        orderItem.order_item_id = UUID(data["order_item_id"])
        return orderItem

    def get_all(self) -> list[OrderItem] | dict:
        all_order_items = []

        data = self._load_data()

        for order_item in data.values():
            product = self.product_repository.get(
                UUID(order_item["product_id"])
            )

            all_order_items.append(
                self._from_dict(order_item, product)
            )

        return all_order_items

    def update(self, obj_id: UUID, new_obj: OrderItem) -> OrderItem | dict:

        data = self._load_data()

        if not (new_obj.get_Id() == obj_id):
            raise NotMatchedObjects("Objects are not matched ... ")

        data[str(obj_id)] = new_obj.to_dict()

        with open(self.path, "w") as file:
            json.dump(data, file)

        return new_obj

    def remove(self, obj_id: UUID) -> None | dict:

        data = self._load_data()

        del data[str(obj_id)]

        with open(self.path, "w") as file:
            json.dump(data, file)
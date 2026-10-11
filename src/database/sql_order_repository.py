from decimal import Decimal
from typing import Protocol, Self, Generic, TypeVar
from uuid import UUID
import json

from customer.customer_model import Customer
from exceptions.exceptions_modules import NotMatchedObjects
from order.order_model_module import Order, OrderStatusEnum
from order_item.order_item_module import OrderItem
from repository.repository_protocol import RepositoryProtocol


class SqlOrderRepository:
    def __init__(
        self,
        path,
        customer_repository: RepositoryProtocol,
        order_item_repository: RepositoryProtocol,
        connection,
        table_name: str,
        id_column: str,
    ):
        self.path = path
        self.customer_repository = customer_repository
        self.order_item_repository = order_item_repository
        self.connection = connection
        self.table_name = table_name
        self.id_column = id_column

    # def _load_data(self):
    #     try:
    #         with open(self.path, "r") as file:
    #             content = file.read()

    #         if not content.strip():
    #             return {}

    #         return json.loads(content)

    #     except FileNotFoundError:
    #         return {}

    #     except json.JSONDecodeError:
    #         raise ValueError("Invalid JSON file")

    def add(self, obj_id: UUID, obj: Order) -> Order:
        if not (obj.get_Id() == obj_id):
            raise NotMatchedObjects("Ids are not matching ... ")

        dic_obj = obj.to_dict()
        dic_obj["items_ids"] = json.dumps(dic_obj["items_ids"])
        keys = dic_obj.keys()
        values = dic_obj.values()
        placeholders = ", ".join(["?"] * len(keys))
        query = f"insert into {(self.table_name)} ({", ".join(keys)}) values ({placeholders})"
        self.connection.cursor().execute(query, tuple(values))
        self.connection.commit()

        return obj

    def get(self, obj_id: UUID) -> Order | None:

        cursor = self.connection.cursor()
        query = f"select * from {self.table_name} where {self.id_column} = ?"
        result = cursor.execute(query, (str(obj_id),)).fetchone()
        if result is None:
            return None
        else:
            columns = [column[0] for column in cursor.description]

            data = dict(zip(columns, result))
            customer = self.customer_repository.get(UUID(data["customer_id"]))
            items = []
            for i in json.loads(data["items_ids"]):
                item = self.order_item_repository.get(UUID(str(i)))
                items.append(item)

            return self._from_dict(data, customer, items)

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
        cursor = self.connection.cursor()
        query = f"select * from {self.table_name} "
        result = cursor.execute(query).fetchall()
        columns = [column[0] for column in cursor.description]

        for order in result:
            items = []
            data = dict(zip(columns, order))
            customer = self.customer_repository.get(UUID(data["customer_id"]))
            for j in json.loads(data["items_ids"]):
                item = self.order_item_repository.get(UUID(str(j)))
                items.append(item)
            dic_data = self._from_dict(data, customer, items)
            all_orders.append(dic_data)

        return all_orders

    def update(self, obj_id: UUID, new_obj: Order) -> Order:

        if not (new_obj.get_Id() == obj_id):
            raise NotMatchedObjects("Ids are not matching ... ")
        cursor = self.connection.cursor()

        new_dict_obj = {}
        dic_obj = new_obj.to_dict()
        dic_obj["items_ids"] = json.dumps(dic_obj["items_ids"])
        for key, value in dic_obj.items():
            if key == self.id_column :
                continue
            else:
                new_dict_obj[key] = value

        keys = new_dict_obj.keys()
        values = new_dict_obj.values()
        query = f"update {self.table_name} set {"=?,".join(keys)} =? where {self.id_column}=(?)"
        cursor.execute(query, (*values, str(obj_id)))
        self.connection.commit()
        return new_obj

    def remove(self, obj_id: UUID) -> None:
        cursor = self.connection.cursor()
        query = f"delete from {self.table_name} where  {self.id_column} = ?"
        cursor.execute(query, (str(obj_id),))
        self.connection.commit()

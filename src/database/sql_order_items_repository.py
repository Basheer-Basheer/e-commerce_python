from decimal import Decimal
from uuid import UUID

from product.product_model import Product
from order_item.order_item_module import OrderItem
from repository.repository_protocol import RepositoryProtocol
from exceptions.exceptions_modules import NotMatchedObjects


class SqlOrderItemsRepository:
    def __init__(
        self,
        connection,
        product_repository: RepositoryProtocol,
        table_name: str,
        id_column: str,
    ):
        self.connection = connection
        self.product_repository = product_repository
        self.table_name = table_name
        self.id_column = id_column

    def add(self, obj_id: UUID, obj: OrderItem) -> OrderItem:
        if obj.get_Id() != obj_id:
            raise NotMatchedObjects("Ids are not matching ...")

        data = obj.to_dict()

        cursor = self.connection.cursor()

        keys = list(data.keys())
        values = list(data.values())
        placeholders = ", ".join(["?"] * len(keys))

        query = (
            f"INSERT INTO {self.table_name} "
            f"({', '.join(keys)}) VALUES ({placeholders})"
        )

        cursor.execute(query, tuple(values))
        self.connection.commit()

        return obj

    def get(self, obj_id: UUID) -> OrderItem | None:
        cursor = self.connection.cursor()

        query = (
            f"SELECT * FROM {self.table_name} "
            f"WHERE {self.id_column} = ?"
        )

        result = cursor.execute(
            query, (str(obj_id),)
        ).fetchone()

        if result is None:
            return None

        columns = [
            column[0] for column in cursor.description
        ]
        data = dict(zip(columns, result))

        product = self.product_repository.get(
            UUID(data["product_id"])
        )

        if product is None:
            return None

        return self._from_dict(data, product)

    def _from_dict(
        self,
        data: dict,
        product: Product,
    ) -> OrderItem:
        item = OrderItem(
            product=product,
            quantity=data["quantity"],
        )

        item.unit_price = Decimal(data["unit_price"])
        item.order_item_id = UUID(data["order_item_id"])

        return item

    def get_all(self) -> list[OrderItem]:
        cursor = self.connection.cursor()

        query = f"SELECT * FROM {self.table_name}"
        result = cursor.execute(query).fetchall()

        columns = [
            column[0] for column in cursor.description
        ]

        items = []

        for row in result:
            data = dict(zip(columns, row))

            product = self.product_repository.get(
                UUID(data["product_id"])
            )

            if product is None:
                continue

            items.append(self._from_dict(data, product))

        return items

    def update(
        self,
        obj_id: UUID,
        new_obj: OrderItem,
    ) -> OrderItem:
        if new_obj.get_Id() != obj_id:
            raise NotMatchedObjects(
                "Objects are not matched ..."
            )

        data = new_obj.to_dict()

        # استثناء حقل المعرّف من التحديث
        update_data = {
            key: value
            for key, value in data.items()
            if key != self.id_column
        }

        keys = list(update_data.keys())
        values = list(update_data.values())

        assignments = ", ".join(
            f"{key} = ?" for key in keys
        )

        query = (
            f"UPDATE {self.table_name} "
            f"SET {assignments} "
            f"WHERE {self.id_column} = ?"
        )

        cursor = self.connection.cursor()
        cursor.execute(
            query, (*values, str(obj_id))
        )
        self.connection.commit()

        return new_obj

    def remove(self, obj_id: UUID) -> None:
        cursor = self.connection.cursor()

        query = (
            f"DELETE FROM {self.table_name} "
            f"WHERE {self.id_column} = ?"
        )

        cursor.execute(query, (str(obj_id),))
        self.connection.commit()

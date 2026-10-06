from typing import Generic, Protocol, TypeVar, Self
from uuid import UUID
import json

from customer.customer_model import Customer
from exceptions.exceptions_modules import NotMatchedObjects
from product.product_model import Product


class Serializable(Protocol):
    def to_dict(self) -> dict: ...

    def get_id(self) -> UUID: ...

    @classmethod
    def from_dict(cls, data: dict) -> Self: ...


T = TypeVar("T", bound=Serializable)


class JsonRepository(Generic[T]):
    def __init__(self, path: str, model: type[T]) -> None:
        self.path = path
        self.model = model

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

    def add(self, obj_id: UUID, obj: T) -> T:
        data = self._load_data()

        added_dict = obj.to_dict()
        data[str(obj_id)] = added_dict

        with open(self.path, "w") as file:
            json.dump(data, file)

        return obj

    def get(self, obj_id: UUID) -> T:
        data = self._load_data()

        item = data[str(obj_id)]

        return self.model.from_dict(item)

    def get_all(self) -> list[T]:
        data_list: list[T] = []

        data = self._load_data()

        for obj in data.values():
            data_list.append(self.model.from_dict(obj))

        return data_list

    def update(self, obj_id: UUID, new_obj: T) -> T:
        data = self._load_data()

        if not (new_obj.get_id() == obj_id):
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

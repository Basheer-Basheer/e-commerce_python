from typing import Generic, TypeVar
from uuid import UUID

from exceptions.exceptions_modules import ItemNotFoundError

T = TypeVar("T")


class InMemoryRepository(Generic[T]):
    def __init__(self) -> None:
        self.items: dict[UUID, T] = {}

    def add(self, obj_id: UUID, obj: T) -> T:
        self.items[obj_id] = obj
        return obj

    def get(self, obj_id: UUID) -> T:
        try:
            obj = self.items[obj_id]
            return obj
        except KeyError:
            raise ItemNotFoundError("Item not found")

    def get_all(self) -> list[T]:
        return list(self.items.values())

    def update(self, obj_id: UUID, new_obj: T) -> T:
        try:
            item = self.items[obj_id]
            self.items[obj_id] = new_obj
            return new_obj
        except KeyError:
            raise ItemNotFoundError("Item not found")

    def remove(self, obj_id: UUID) -> None:
        try:
            del self.items[obj_id]
        except KeyError:
            raise ItemNotFoundError("item not found")

from typing import Protocol, TypeVar, Generic
from uuid import UUID

T = TypeVar("T")


class RepositoryProtocol(Protocol, Generic[T]):
    
    
    def add(self, obj_id: UUID, obj: T) -> T:
        ...
    
    def get(self, obj_id:UUID) -> T:
        ...
        
    def get_all(self) -> list[T]:
        ...
    def update(self, obj_id:UUID, new_obj: T)-> T :
        ...
    def remove(self, obj_id:UUID) -> None:
        ...
from typing import TypeVar, Generic, Protocol, Self
from uuid import UUID

from exceptions.exceptions_modules import NotMatchedObjects


class Serializable(Protocol):
    def to_dict(self) -> dict: ...

    def get_id(self) -> UUID: ...

    @classmethod
    def from_dict(cls, data: dict) -> Self: ...


T = TypeVar("T", bound=Serializable)


class SqlRepository(Generic[T]):
    def __init__(self, connection, model: type[T], table_name: str, id_column:str) -> None:
        self.connection = connection
        self.table_name = table_name
        self.model = model
        self.id_column = id_column

    def add(self, obj_id: UUID, obj: T) -> T:
        dic_obj = obj.to_dict()
        keys = dic_obj.keys()
        values = dic_obj.values()
        placeholders = ", ".join(["?"] * len(keys))
        query = f"insert into {(self.table_name)} ({", ".join(keys)}) values ({placeholders})"
        self.connection.cursor().execute(query, tuple(values))
        self.connection.commit()

        return obj

    def get(self, obj_id: UUID) -> T | None:
        cursor = self.connection.cursor()
        query = f"select * from {self.table_name} where {self.id_column} = ?"
        result = cursor.execute(query, (str(obj_id),)).fetchone()
        if result is None:
            return None
        else:
            columns = [column[0] for column in cursor.description]

            data = dict(zip(columns, result))

            return self.model.from_dict(data)

    def get_all(self) -> list[T]:

        cursor = self.connection.cursor()
        query = f"select * from {self.table_name} "
        result = cursor.execute(query).fetchall()
        all_data = []
        columns = [column[0] for column in cursor.description]
        for i in result:
            data = dict(zip(columns, i))
            dic_data = self.model.from_dict(data)
            all_data.append(dic_data)

        return all_data

    def update(self, obj_id: UUID, new_obj: T) -> T:
        if new_obj.get_id() != obj_id:
            raise NotMatchedObjects("Objects are not matched")
        cursor = self.connection.cursor()
        dic_obj = new_obj.to_dict()

        new_dict_obj = {}
        for key, value in dic_obj.items():
            if value == str(obj_id) and new_obj.get_id() == obj_id:
                continue
            else:
                new_dict_obj[key] = value

        keys = new_dict_obj.keys()
        values = list(new_dict_obj.values())

        query = f"update {self.table_name} set {"=?,".join(keys)} =? where {self.id_column}=(?)"
        cursor.execute(query, tuple(values + [str(obj_id)]))
        self.connection.commit()
        return new_obj

    def remove(self, obj_id: UUID) -> None:
        cursor = self.connection.cursor()
        query = f"delete from {self.table_name} where  {self.id_column} = ?"
        cursor.execute(
            query,
            (
                (str(
                    obj_id
                ),)
            ),
        )
        self.connection.commit()

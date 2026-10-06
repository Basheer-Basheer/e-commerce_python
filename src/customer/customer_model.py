from typing import Protocol, runtime_checkable
from uuid import UUID, uuid4
from dataclasses import dataclass, field
from enum import Enum, auto
import uuid

from product.product_model import ProductStatusEnum

class CustomerStatusEnum(Enum):
    ACTIVE = auto()
    INACTIVE = auto()
    BLOCKED = auto()


@dataclass
class Customer:
    name: str
    email: str
    phone: str
    customer_id: UUID = field(init=False, default_factory=uuid4)
    status: CustomerStatusEnum = CustomerStatusEnum.ACTIVE

    def __post_init__(self, ):
        if not isinstance(self.name, str):
            raise TypeError("Name must be string")
        elif self.name.strip() == "":
            raise ValueError("Name must be string")
        elif not isinstance(self.email, str):
            raise TypeError("Email must be string")

        elif self.email.strip() == "":
            raise ValueError("Email must be string")
        elif not isinstance(self.phone, str):
            raise TypeError("Phone must be string")
        elif self.phone.strip() == "":
            raise ValueError("Phone must be string")



    def to_dict(self) -> dict:
        data ={
                "customer_id" : str(self.customer_id),
                "name" : self.name,
                "email" : self.email,
                "phone" : self.phone,
                "status" : self.status.name,
                
            }
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> Customer:    
        customer :Customer = Customer(
          name=data["name"],
          email=data["email"],
          phone=data["phone"],
          status=data["status"],
        )
        customer.customer_id = uuid.UUID(data["customer_id"])
        
        return customer

    def get_id(self) -> uuid.UUID :
        return self.customer_id
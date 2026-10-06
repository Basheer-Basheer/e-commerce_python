from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum, auto
from uuid import UUID, uuid4

from customer.customer_model import Customer
from exceptions.exceptions_modules import ItemNotFoundError, OrderStatusError
from order_item.order_item_module import OrderItem


class OrderStatusEnum(Enum):
    PENDING = auto()
    CONFIRMED = auto()
    PAID = auto()
    SHIPPED = auto()
    COMPLETED = auto()
    CANCELLED = auto()


@dataclass
class Order:
    customer: Customer
    discount: Decimal = field(init=False, default=Decimal("0.00"))
    items: list[OrderItem] = field(default_factory=list)
    order_id: UUID = field(init=False, default_factory=uuid4)
    status: OrderStatusEnum = OrderStatusEnum.PENDING
    created_date: str = field(
        init=False, default_factory=lambda: datetime.today().isoformat()
    )

    def add_item(self, order_item: OrderItem) -> OrderItem:
        if not isinstance(order_item, OrderItem):
            raise TypeError("order_item must be an OrderItem")
        if self.status is not OrderStatusEnum.PENDING:
            raise OrderStatusError("Can not do anything because of order status")
        self.items.append(order_item)
        return order_item

    def remove_item(self, order_item_id: UUID) -> OrderItem:
        for index, item in enumerate(self.items):
            if item.order_item_id == order_item_id:
                removed_item = self.items.pop(index)
                return removed_item
        raise ItemNotFoundError("Item does not exist")

    def calculate_subtotal(self) -> Decimal:
        return sum((item.subtotal() for item in self.items), Decimal("0.00"))

    def calculate_total(self) -> Decimal:
        return self.calculate_subtotal() - self.discount

    def add_discount(self, amount: Decimal) -> None:
        if not isinstance(amount, Decimal):
            raise TypeError("Please insert a decimal num")
        if amount < 0:
            raise ValueError("Please insert a valid discount")
        self.discount = amount



    def to_dict(self) -> dict:
        data ={
                "customer_id" : str(self.customer.customer_id),
                "discount" : str(self.discount),
                "items_ids": [str(i.order_item_id) for i in self.items],
                "order_id" : str(self.order_id),
                "status" : self.status.name,
                "created_date" : str(self.created_date),
                
            }
        return data
    
   

    def get_Id(self)-> UUID:
        return self.order_id
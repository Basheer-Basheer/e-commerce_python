from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from enum import Enum, auto
import uuid

from exceptions.exceptions_modules import InsufficientStockAmount, InvalidProductStatusError


class ProductStatusEnum(Enum):
    ACTIVE = auto()
    INACTIVE = auto()
    DISCONTINUED = auto()


class ProductCategoryEnum(Enum):
    ELECTRONICS = auto()
    CLOTHING = auto()
    FOOD = auto()
    HOME = auto()
    OTHER = auto()


@dataclass
class Product:
    name: str
    description: str
    price: Decimal
    stock: int
    category: ProductCategoryEnum
    product_id: uuid.UUID = field(init=False, default_factory=uuid.uuid4)
    status: ProductStatusEnum = ProductStatusEnum.ACTIVE

    def __post_init__(
            self,
    ) -> None:
        if not isinstance(self.name, str):
            raise TypeError("Product name must be a string")
        if self.name.strip() == "":
            raise ValueError("The product name should be not an empty string .... ")

        if not isinstance(self.price, Decimal):
            try:
                self.price = Decimal(str(self.price)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            except InvalidOperation:
                raise ValueError("Please insert a valid operator")
        if self.price <= 0:
            raise ValueError("Price should be more than 'ZERO'")

        if self.stock < 0:
            raise ValueError("Stock should be more than 'ZERO'")

    def activate(self) -> None:
        if self.status is ProductStatusEnum.ACTIVE:
            raise ValueError("Product is already active")

        self.status = ProductStatusEnum.ACTIVE

    def deactivate(self) -> None:
        if self.status is ProductStatusEnum.INACTIVE:
            raise ValueError("Product is already inactive")

        self.status = ProductStatusEnum.INACTIVE

    def discontinue(self) -> None:
        if self.status is ProductStatusEnum.DISCONTINUED:
            raise ValueError("Product is already discontinued")

        self.status = ProductStatusEnum.DISCONTINUED

    def increase_stock(self, amount: int) -> None:
        if self.status in (ProductStatusEnum.DISCONTINUED,):
            raise InvalidProductStatusError("this product is can not be increased")
        if not isinstance(amount, int):
            raise TypeError("Please enter (int) argument")
        if amount <= 0:
            raise ValueError("amount must be more than zero")
        self.stock += amount

    def decrease_stock(self, amount: int) -> None:
        if not isinstance(amount, int):
            raise TypeError("Please enter (int) argument")
        if amount <= 0:
            raise ValueError("amount must be more than zero")

        if self.status in (ProductStatusEnum.DISCONTINUED, ProductStatusEnum.INACTIVE):
            raise InvalidProductStatusError("this product is can not be sold")
        if self.stock < amount:
            raise InsufficientStockAmount("Amount should not be more than stock")
        self.stock -= amount



    def is_active(self)-> bool:
        return self.status is ProductStatusEnum.ACTIVE

    def is_available(self, amount: int) -> bool:
        return (
            self.is_active()
            and isinstance(amount, int)
            and amount > 0
            and amount <= self.stock
        )
        
        
    def to_dict(self) -> dict:
        data ={
                "product_id" : str(self.product_id),
                "name" : str(self.name),
                "description" : str(self.description),
                "price" : str(self.price),
                "stock" : self.stock,
                "category" : str(self.category.name),
                "status" : str(self.status.name),
            }
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> Product:    
        product :Product = Product(
            name=data["name"],
            description=data["description"],
            price=Decimal(data["price"]),
            stock=data["stock"],
            category=ProductCategoryEnum[data["category"]],
            status=ProductStatusEnum[data["status"]],
        )
        product.product_id = uuid.UUID(data["product_id"])
        
        return product

    def get_id(self) -> uuid.UUID :
        return self.product_id
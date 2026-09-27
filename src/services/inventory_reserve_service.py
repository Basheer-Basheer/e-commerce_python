from uuid import UUID

from product.product_model import Product
from repository.repository_protocol import RepositoryProtocol


class InventoryService:
    def __init__(self, product_repository: RepositoryProtocol[Product]):
        self.product_repository = product_repository

    def reserve_stock(self, product_id: UUID, quantity: int) -> None:
        product = self.product_repository.get(product_id)
        product.decrease_stock(quantity)
        self.product_repository.update(product_id, product)

    def release_stock(self, product_id: UUID, quantity: int) -> None:
        product = self.product_repository.get(product_id)
        product.increase_stock(quantity)
        self.product_repository.update(product_id, product)

    def confirm_stock(self, product_id: UUID, quantity: int) -> None:
        pass



from uuid import UUID

from product.product_model import Product
from repository.repository_protocol import RepositoryProtocol


class ProductService:
    def __init__(self,product_repository: RepositoryProtocol[Product]) -> None:
        self.product_repository = product_repository
        
        
       
    def add_product(self,product_id : UUID, product:Product) -> Product:
        self.product_repository.add(product_id,product)
        return product
        
        
    def get_product(self,product_id : UUID) -> Product:
        product = self.product_repository.get(product_id)
        return product
    
    def list_products(self,) -> list[Product]:
        return self.product_repository.get_all()
        
        
    def remove_product(self,product_id : UUID) -> None:
        self.product_repository.remove(product_id)
        
    def update_product(self, product_id: UUID, new_product: Product) -> Product:
        updated_product = self.product_repository.update(product_id,new_product)
        return updated_product
        
        
    def activate_product(self,product_id : UUID) -> None:
        product:Product = self.product_repository.get(product_id)
        product.activate()
        self.product_repository.update(product.product_id, product)
        
    def deactivate_product(self,product_id : UUID) -> None:
        product:Product = self.product_repository.get(product_id)
        product.deactivate()
        self.product_repository.update(product.product_id, product)
       
       
    def discontinue_product(self,product_id : UUID) -> None:
        product:Product = self.product_repository.get(product_id)
        product.discontinue()
        self.product_repository.update(product.product_id, product)
       
       
       
        
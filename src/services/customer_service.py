



from uuid import UUID

from customer.customer_model import Customer
from repository.repository_protocol import RepositoryProtocol


class CustomerService:
    def __init__(self, customer_repository:RepositoryProtocol[Customer]) -> None:
        self.customer_repository = customer_repository
        
        
        
    def add_customer(self,customer_id : UUID, customer:Customer) -> Customer:
        self.customer_repository.add(customer_id,customer)
        return customer
        
        
    def get_customer(self,customer_id : UUID) -> Customer:
        customer = self.customer_repository.get(customer_id)
        return customer
    
    def list_customers(self,) -> list[Customer]:
        return self.customer_repository.get_all()
        
        
    def remove_customer(self,customer_id : UUID) -> None:
        self.customer_repository.remove(customer_id)
        
    def update_customer(self, customer_id: UUID, new_customer: Customer) -> Customer:
        updated_customer = self.customer_repository.update(customer_id,new_customer)
        return updated_customer
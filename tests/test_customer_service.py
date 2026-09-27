import pytest
from uuid import uuid4

from customer.customer_model import Customer
from repository.inmemoryrepository import InMemoryRepository
from repository.repository_protocol import RepositoryProtocol
from services.customer_service import CustomerService
from exceptions.exceptions_modules import ItemNotFoundError


@pytest.fixture
def service():
    repo : RepositoryProtocol[Customer] = InMemoryRepository[Customer]()
    return CustomerService(repo)


@pytest.fixture
def sample_customer():
    return Customer(
       email="basher.fadi.basher@gmail.com",
       name="basheer",
       phone="01015803348",
    )


def test_add_customer(service, sample_customer):
    result = service.add_customer(sample_customer.customer_id, sample_customer)
    assert result == sample_customer


def test_get_customer(service, sample_customer):
    service.add_customer(sample_customer.customer_id, sample_customer)
    fetched = service.get_customer(sample_customer.customer_id)
    assert fetched == sample_customer


def test_get_missing_customer_raises(service):
    with pytest.raises(ItemNotFoundError):
        service.get_customer(uuid4())


def test_list_customers(service, sample_customer):
    service.add_customer(sample_customer.customer_id, sample_customer)
    customers = service.list_customers()
    assert len(customers) == 1
    assert sample_customer in customers


def test_remove_customer(service, sample_customer):
    service.add_customer(sample_customer.customer_id, sample_customer)
    service.remove_customer(sample_customer.customer_id)
    with pytest.raises(ItemNotFoundError):
        service.get_customer(sample_customer.customer_id)


def test_remove_missing_customer_raises(service):
    with pytest.raises(ItemNotFoundError):
        service.remove_customer(uuid4())


def test_update_customer(service, sample_customer):
    service.add_customer(sample_customer.customer_id, sample_customer)
    sample_customer.email = "b@gmail.com"
    updated = service.update_customer(sample_customer.customer_id, sample_customer)
    assert updated.email == "b@gmail.com"
    assert service.get_customer(sample_customer.customer_id).email == "b@gmail.com"


def test_update_missing_customer_raises(service, sample_customer):
    with pytest.raises(ItemNotFoundError):
        service.update_customer(uuid4(), sample_customer)


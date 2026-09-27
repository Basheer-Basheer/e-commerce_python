import pytest
from decimal import Decimal
from uuid import uuid4

from product.product_model import Product, ProductCategoryEnum
from repository.inmemoryrepository import InMemoryRepository
from repository.repository_protocol import RepositoryProtocol
from services.product_service import ProductService
from exceptions.exceptions_modules import ItemNotFoundError


@pytest.fixture
def service():
    repo :RepositoryProtocol[Product] = InMemoryRepository[Product]()
    return ProductService(repo)


@pytest.fixture
def sample_product():
    return Product(
        name="Mouse",
        description="Gaming mouse",
        price=Decimal("150.00"),
        stock=10,
        category=ProductCategoryEnum.ELECTRONICS,
    )


def test_add_product(service, sample_product):
    result = service.add_product(sample_product.product_id, sample_product)
    assert result == sample_product


def test_get_product(service, sample_product):
    service.add_product(sample_product.product_id, sample_product)
    fetched = service.get_product(sample_product.product_id)
    assert fetched == sample_product


def test_get_missing_product_raises(service):
    with pytest.raises(ItemNotFoundError):
        service.get_product(uuid4())


def test_list_products(service, sample_product):
    service.add_product(sample_product.product_id, sample_product)
    products = service.list_products()
    assert len(products) == 1
    assert sample_product in products


def test_remove_product(service, sample_product):
    service.add_product(sample_product.product_id, sample_product)
    service.remove_product(sample_product.product_id)
    with pytest.raises(ItemNotFoundError):
        service.get_product(sample_product.product_id)


def test_remove_missing_product_raises(service):
    with pytest.raises(ItemNotFoundError):
        service.remove_product(uuid4())


def test_update_product(service, sample_product):
    service.add_product(sample_product.product_id, sample_product)
    sample_product.price = Decimal("200.00")
    updated = service.update_product(sample_product.product_id, sample_product)
    assert updated.price == Decimal("200.00")
    assert service.get_product(sample_product.product_id).price == Decimal("200.00")


def test_update_missing_product_raises(service, sample_product):
    with pytest.raises(ItemNotFoundError):
        service.update_product(uuid4(), sample_product)


def test_activate_product(service, sample_product):
    sample_product.deactivate()
    service.add_product(sample_product.product_id, sample_product)
    service.activate_product(sample_product.product_id)
    assert service.get_product(sample_product.product_id).status.name == "ACTIVE"


def test_deactivate_product(service, sample_product):
    service.add_product(sample_product.product_id, sample_product)
    service.deactivate_product(sample_product.product_id)
    assert service.get_product(sample_product.product_id).status.name == "INACTIVE"


def test_discontinue_product(service, sample_product):
    service.add_product(sample_product.product_id, sample_product)
    service.discontinue_product(sample_product.product_id)
    assert service.get_product(sample_product.product_id).status.name == "DISCONTINUED"


def test_activate_missing_product_raises(service):
    with pytest.raises(ItemNotFoundError):
        service.activate_product(uuid4())
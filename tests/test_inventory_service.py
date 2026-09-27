import pytest
from decimal import Decimal

from product.product_model import Product, ProductCategoryEnum
from repository.inmemoryrepository import InMemoryRepository
from services.inventory_reserve_service import InventoryService
from exceptions.exceptions_modules import InsufficientStockAmount


@pytest.fixture
def product_repo():
    return InMemoryRepository[Product]()


@pytest.fixture
def inventory_service(product_repo):
    return InventoryService(product_repo)


@pytest.fixture
def sample_product(product_repo):
    product = Product(
        name="Mouse",
        description="Gaming mouse",
        price=Decimal("100.00"),
        stock=10,
        category=ProductCategoryEnum.ELECTRONICS,
    )
    product_repo.add(product.product_id, product)
    return product


def test_successful_reservation(inventory_service, sample_product, product_repo):
    inventory_service.reserve_stock(sample_product.product_id, 3)

    updated_product = product_repo.get(sample_product.product_id)
    assert updated_product.stock == 7


def test_failed_reservation_insufficient_stock(inventory_service, sample_product):
    with pytest.raises(InsufficientStockAmount):
        inventory_service.reserve_stock(sample_product.product_id, 999)


def test_payment_failure_releases_stock(inventory_service, sample_product, product_repo):
    inventory_service.reserve_stock(sample_product.product_id, 3)
    # المخزون هلق 7

    inventory_service.release_stock(sample_product.product_id, 3)

    updated_product = product_repo.get(sample_product.product_id)
    assert updated_product.stock == 10  # رجع لأصله


def test_successful_payment_confirms_stock(inventory_service, sample_product, product_repo):
    inventory_service.reserve_stock(sample_product.product_id, 3)
    # المخزون هلق 7

    inventory_service.confirm_stock(sample_product.product_id, 3)

    updated_product = product_repo.get(sample_product.product_id)
    assert updated_product.stock == 7  # ما تغير شي إضافي، لأن confirm فاضية


def test_reservation_fails_when_stock_exactly_insufficient(inventory_service, sample_product):
    with pytest.raises(InsufficientStockAmount):
        inventory_service.reserve_stock(sample_product.product_id, 11)  # أكبر بواحد من المتاح
import pytest
from uuid import uuid4
from decimal import Decimal

from repository.Inmemoryrepository import InMemoryRepository
from product.product_model import Product, ProductCategoryEnum
from exceptions.exceptions_modules import ItemNotFoundError


@pytest.fixture
def repo():
    return InMemoryRepository[Product]()


@pytest.fixture
def sample_product():
    return Product(
        name="Mouse",
        description="Gaming mouse",
        price=Decimal("150.00"),
        stock=10,
        category=ProductCategoryEnum.ELECTRONICS,
    )


def test_add_and_get(repo, sample_product):
    repo.add(sample_product.product_id, sample_product)
    result = repo.get(sample_product.product_id)
    assert result == sample_product


def test_get_missing_item_raises(repo):
    with pytest.raises(ItemNotFoundError):
        repo.get(uuid4())


def test_get_all(repo, sample_product):
    repo.add(sample_product.product_id, sample_product)
    all_items = repo.get_all()
    assert len(all_items) == 1
    assert sample_product in all_items


def test_update_existing_item(repo, sample_product):
    repo.add(sample_product.product_id, sample_product)
    sample_product.price = Decimal("200.00")
    updated = repo.update(sample_product.product_id, sample_product)
    assert repo.get(sample_product.product_id).price == Decimal("200.00")


def test_update_missing_item_raises(repo):
    fake_product = Product(
        name="Ghost", description="not real", price=Decimal("1.00"),
        stock=1, category=ProductCategoryEnum.OTHER,
    )
    with pytest.raises(ItemNotFoundError):
        repo.update(uuid4(), fake_product)


def test_remove_existing_item(repo, sample_product):
    repo.add(sample_product.product_id, sample_product)
    repo.remove(sample_product.product_id)
    with pytest.raises(ItemNotFoundError):
        repo.get(sample_product.product_id)


def test_remove_missing_item_raises(repo):
    with pytest.raises(ItemNotFoundError):
        repo.remove(uuid4())
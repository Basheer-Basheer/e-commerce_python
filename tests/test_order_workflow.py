import pytest
from decimal import Decimal

from customer.customer_model import Customer
from product.product_model import Product, ProductCategoryEnum
from order.order_model_module import Order, OrderStatusEnum
from cart.cart_model import Cart
from repository.notification_prorocol import NotificationService
from repository.payment_protocol import Payment, FakePaymentProcessor
from repository.inmemoryrepository import InMemoryRepository
from services.order_service import OrderService
from services.checkout_service import CheckoutService
from services.inventory_reserve_service import InventoryService

from repository.payment_protocol import PaymentService
from orderworkflowservice.order_workflow_service import OrderWorkflowService
from repository.discount_protocol import NoDiscount
from exceptions.exceptions_modules import UnexpectedPaymentStatusError
from orderworkflowservice.order_workflow_service import OrderWorkflowService


@pytest.fixture
def product_repo():
    return InMemoryRepository[Product]()


@pytest.fixture
def customer_repo():
    return InMemoryRepository[Customer]()


@pytest.fixture
def order_repo():
    return InMemoryRepository[Order]()


@pytest.fixture
def payment_repo():
    return InMemoryRepository[Payment]()


@pytest.fixture
def order_service(order_repo, customer_repo, product_repo):
    return OrderService(order_repo, customer_repo, product_repo)


@pytest.fixture
def inventory_service(product_repo):
    return InventoryService(product_repo)


@pytest.fixture
def payment_service(payment_repo):
    return PaymentService(payment_repo)


@pytest.fixture
def checkout_service(order_service):
    return CheckoutService(order_service, discount=NoDiscount())


@pytest.fixture
def notification_service():
    from unittest.mock import Mock
    fake_notification = Mock()
    return NotificationService(notification=fake_notification)


@pytest.fixture
def workflow_service(checkout_service, inventory_service, payment_service, notification_service, order_service):
    return OrderWorkflowService(
        check_out_service=checkout_service,
        inventory_service=inventory_service,
        payment_service=payment_service,
        notification_service=notification_service,
        order_service=order_service,
    )


@pytest.fixture
def sample_customer(customer_repo):
    customer = Customer(name="Ali", email="ali@test.com", phone="0101234567")
    customer_repo.add(customer.customer_id, customer)
    return customer


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


@pytest.fixture
def cart_with_product(sample_product):
    cart = Cart()
    cart.add_product(sample_product, quantity=2)
    return cart


# ----- Test 1: Complete successful workflow -----

def test_complete_successful_workflow(
    workflow_service, sample_customer, cart_with_product, notification_service, product_repo, sample_product
):
    payment_processor = FakePaymentProcessor(should_succeed=True)

    order, payment = workflow_service.place_order(
        sample_customer.customer_id, cart_with_product, payment_processor
    )

    assert order.status == OrderStatusEnum.CONFIRMED
    assert payment.status.name == "SUCCESS"
    notification_service.notification.send_notification.assert_called_once()

    updated_product = product_repo.get(sample_product.product_id)
    assert updated_product.stock == 8  # كان 10، طلبنا 2


# ----- Test 2: Payment failure -----

def test_payment_failure_cancels_order_and_releases_stock(
    workflow_service, sample_customer, cart_with_product, notification_service, product_repo, sample_product
):
    payment_processor = FakePaymentProcessor(should_succeed=False)

    order, payment = workflow_service.place_order(
        sample_customer.customer_id, cart_with_product, payment_processor
    )

    assert order.status == OrderStatusEnum.CANCELLED
    assert payment.status.name == "FAILED"
    notification_service.notification.send_notification.assert_called_once()

    updated_product = product_repo.get(sample_product.product_id)
    assert updated_product.stock == 10
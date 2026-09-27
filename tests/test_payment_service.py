import pytest
from decimal import Decimal

from customer.customer_model import Customer
from product.product_model import Product, ProductCategoryEnum
from order.order_model_module import Order
from repository.inmemoryrepository import InMemoryRepository
from repository.payment_protocol import (
    Payment,
    PaymentMStatus,
    PaymentMethodEnum,
    CashPaymentProcessor,
    VisaPaymentProcessor,
    BankPaymentProcessor,
    PayPalPaymentProcessor,
    FakePaymentProcessor,
    PaymentService,
)


@pytest.fixture
def payment_repo():
    return InMemoryRepository[Payment]()


@pytest.fixture
def payment_service(payment_repo):
    return PaymentService(payment_repo)


@pytest.fixture
def sample_customer():
    return Customer(name="Ali", email="ali@test.com", phone="0101234567")


@pytest.fixture
def sample_order(sample_customer):
    return Order(customer=sample_customer)


def test_successful_payment_cash(payment_service, sample_customer, sample_order):
    processor = CashPaymentProcessor()
    payment = payment_service.process_payment(
        processor, Decimal("100.00"), sample_customer, sample_order
    )
    assert payment.status == PaymentMStatus.SUCCESS
    assert payment.paymentMethod == PaymentMethodEnum.CASH


def test_payment_stored_in_repository(
    payment_service, payment_repo, sample_customer, sample_order
):
    processor = CashPaymentProcessor()
    payment = payment_service.process_payment(
        processor, Decimal("100.00"), sample_customer, sample_order
    )
    stored = payment_repo.get(payment.payment_id)
    assert stored == payment


def test_failed_payment_using_fake_processor(
    payment_service, sample_customer, sample_order
):
    processor = FakePaymentProcessor(should_succeed=False)
    payment = payment_service.process_payment(
        processor, Decimal("100.00"), sample_customer, sample_order
    )
    assert payment.status == PaymentMStatus.FAILED


def test_successful_payment_using_fake_processor(
    payment_service, sample_customer, sample_order
):
    processor = FakePaymentProcessor(should_succeed=True)
    payment = payment_service.process_payment(
        processor, Decimal("100.00"), sample_customer, sample_order
    )
    assert payment.status == PaymentMStatus.SUCCESS


def test_invalid_amount_type_raises(payment_service, sample_customer, sample_order):
    processor = CashPaymentProcessor()
    with pytest.raises(TypeError):
        payment_service.process_payment(
            processor, 100, sample_customer, sample_order  # int مش Decimal
        )


def test_invalid_amount_negative_raises(payment_service, sample_customer, sample_order):
    processor = CashPaymentProcessor()
    with pytest.raises(ValueError):
        payment_service.process_payment(
            processor, Decimal("-50.00"), sample_customer, sample_order
        )


def test_invalid_amount_zero_raises(payment_service, sample_customer, sample_order):
    processor = CashPaymentProcessor()
    with pytest.raises(ValueError):
        payment_service.process_payment(
            processor, Decimal("0.00"), sample_customer, sample_order
        )


def test_correct_processor_visa(payment_service, sample_customer, sample_order):
    processor = VisaPaymentProcessor(iban="SA1234567890")
    payment = payment_service.process_payment(
        processor, Decimal("100.00"), sample_customer, sample_order
    )
    assert payment.paymentMethod == PaymentMethodEnum.VISA


def test_correct_processor_bank(payment_service, sample_customer, sample_order):
    processor = BankPaymentProcessor(account_number="123456")
    payment = payment_service.process_payment(
        processor, Decimal("100.00"), sample_customer, sample_order
    )
    assert payment.paymentMethod == PaymentMethodEnum.BANK_TRANSFER


def test_correct_processor_paypal(payment_service, sample_customer, sample_order):
    processor = PayPalPaymentProcessor(account_number="paypal@test.com")
    payment = payment_service.process_payment(
        processor, Decimal("100.00"), sample_customer, sample_order
    )
    assert payment.paymentMethod == PaymentMethodEnum.PAYPAL


def test_get_payment(payment_service, sample_customer, sample_order):
    processor = CashPaymentProcessor()
    payment = payment_service.process_payment(
        processor, Decimal("100.00"), sample_customer, sample_order
    )
    fetched = payment_service.get_payment(payment.payment_id)
    assert fetched == payment


def test_get_all_payments(payment_service, sample_customer, sample_order):
    processor = CashPaymentProcessor()
    payment_service.process_payment(
        processor, Decimal("50.00"), sample_customer, sample_order
    )
    payment_service.process_payment(
        processor, Decimal("75.00"), sample_customer, sample_order
    )
    all_payments = payment_service.get_all_payments()
    assert len(all_payments) == 2

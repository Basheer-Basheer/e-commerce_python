from dataclasses import dataclass, field
import datetime
from decimal import Decimal
from enum import Enum, auto
from typing import Protocol
from uuid import UUID, uuid4
from customer.customer_model import Customer
from order.order_model_module import Order
import random
from abc import ABC, abstractmethod

from repository.repository_protocol import RepositoryProtocol


class PaymentMethodEnum(Enum):
    CASH = auto()
    VISA = auto()
    BANK_TRANSFER = auto()
    PAYPAL = auto()
    FAKE = auto()


class PaymentMStatus(Enum):
    PENDING = auto()
    SUCCESS = auto()
    FAILED = auto()


@dataclass
class Payment:
    order: Order
    customer: Customer
    amount: Decimal
    paymentMethod: PaymentMethodEnum
    status: PaymentMStatus
    payment_id: UUID = field(init=False, default_factory=uuid4)
    created_date: str = field(
        init=False, default_factory=lambda: datetime.datetime.today().isoformat()
    )


class PaymentProcessor(ABC):
    def process(self, amount: Decimal, customer: Customer, order: Order) -> Payment:
        if not isinstance(amount, Decimal):
            raise TypeError("Should be a decimal amount")
        if amount <= 0:
            raise ValueError("Amount should be more than zero")
        if customer is None or not isinstance(customer, Customer):
            raise ValueError("Receuiver should be a valid")

        status = self._determine_status()

        return Payment(
            order=order,
            customer=customer,
            amount=amount,
            paymentMethod=self._get_method(),
            status=status,
        )

    @abstractmethod
    def _determine_status(
        self,
    ) -> PaymentMStatus: ...

    @abstractmethod
    def _get_method(
        self,
    ) -> PaymentMethodEnum: ...


class CashPaymentProcessor(PaymentProcessor):
    def _determine_status(
        self,
    ) -> PaymentMStatus:
        return PaymentMStatus.SUCCESS

    def _get_method(
        self,
    ) -> PaymentMethodEnum:
        return PaymentMethodEnum.CASH


class VisaPaymentProcessor(PaymentProcessor):
    def __init__(self, iban: str) -> None:
        self.iban = iban

    def _determine_status(
        self,
    ) -> PaymentMStatus:
        result = random.random()
        return PaymentMStatus.SUCCESS if result < 0.9 else PaymentMStatus.FAILED

    def _get_method(
        self,
    ) -> PaymentMethodEnum:
        return PaymentMethodEnum.VISA


class BankPaymentProcessor(PaymentProcessor):
    def __init__(self, account_number: str) -> None:
        self.account_number = account_number

    def _determine_status(
        self,
    ) -> PaymentMStatus:
        result = random.random()
        return PaymentMStatus.SUCCESS if result < 0.9 else PaymentMStatus.FAILED

    def _get_method(
        self,
    ) -> PaymentMethodEnum:
        return PaymentMethodEnum.BANK_TRANSFER


class PayPalPaymentProcessor(PaymentProcessor):
    def __init__(self, account_number: str) -> None:
        self.account_number = account_number

    def _determine_status(
        self,
    ) -> PaymentMStatus:
        result = random.random()
        return PaymentMStatus.SUCCESS if result < 0.9 else PaymentMStatus.FAILED

    def _get_method(
        self,
    ) -> PaymentMethodEnum:
        return PaymentMethodEnum.PAYPAL


class FakePaymentProcessor(PaymentProcessor):
    def __init__(self, should_succeed: bool = True) -> None:
        self.should_succeed = should_succeed

    def _determine_status(self) -> PaymentMStatus:
        return PaymentMStatus.SUCCESS if self.should_succeed else PaymentMStatus.FAILED

    def _get_method(self) -> PaymentMethodEnum:
        return PaymentMethodEnum.FAKE


class PaymentService:
    def __init__(self, payments_repository: RepositoryProtocol[Payment]) -> None:
        self.payments_repository = payments_repository
    
    
    def process_payment(
        self,
        paymentProcessor: PaymentProcessor,
        amount: Decimal,
        customer: Customer,
        order: Order,
    ) -> Payment:
        payment = paymentProcessor.process(amount, customer, order)
        self.payments_repository.add(payment.payment_id, payment)
        return payment

    def get_payment(self, payment_id:UUID) -> Payment:
        payment = self.payments_repository.get(payment_id)
        return payment
    
    
    def get_all_payments(self,) -> list[Payment]:
        return self.payments_repository.get_all()
    
    
from typing import Protocol

from order.order_model_module import Order
from repository.payment_protocol import Payment


class NotificationProtocol(Protocol):

    def send_notification(self, receiver: str, message: str):
        ...


class SmsNotification:

    def send_notification(self, receiver: str, message: str):
        print(f"Sending SMS Message to {receiver}: {message}")


class EmailNotification:

    def send_notification(self, receiver: str, message: str):
        print(f"Sending Email to {receiver}: {message}")


class WhatsAppNotification:

    def send_notification(self, receiver: str, message: str):
        print(f"Sending WhatsApp Message to {receiver}: {message}")


class NotificationService:

    def __init__(self, notification: NotificationProtocol) -> None:
        self.notification = notification

    def make_notification(self, receiver: str, message: str):
        if not isinstance(receiver, str) or not isinstance(message, str):
            raise TypeError("receiver and message should be strings")

        if receiver.strip() == "" or message.strip() == "":
            raise ValueError("receiver and message shouldn't be empty")

        self.notification.send_notification(receiver, message)

    def order_created(self, receiver: str, order: Order):
        if not isinstance(receiver, str):
            raise TypeError("receiver should be a string")

        if not isinstance(order, Order):
            raise TypeError("order should be an instance of Order class")

        if receiver.strip() == "":
            raise ValueError("receiver shouldn't be empty")

        message = (
            f"Order ID {order.order_id} has been successfully created "
            f"with total {order.calculate_total()} ..."
        )

        self.notification.send_notification(receiver, message)

    def payment_successful(self, receiver: str, payment: Payment):
        if not isinstance(receiver, str):
            raise TypeError("receiver should be a string")

        if not isinstance(payment, Payment):
            raise TypeError("payment should be an instance of Payment class")

        if receiver.strip() == "":
            raise ValueError("receiver shouldn't be empty")

        message = (
            f"Payment reference is: "
            f"{payment.payment_id}-{payment.paymentMethod.name} "
            f"has been successfully paid ..."
        )

        self.notification.send_notification(receiver, message)

    def payment_failed(self, receiver: str, payment: Payment):
        if not isinstance(receiver, str):
            raise TypeError("receiver should be a string")

        if not isinstance(payment, Payment):
            raise TypeError("payment should be an instance of Payment class")

        if receiver.strip() == "":
            raise ValueError("receiver shouldn't be empty")

        message = (
            f"Payment reference is: "
            f"{payment.payment_id}-{payment.paymentMethod.name} "
            f"has failed ..."
        )

        self.notification.send_notification(receiver, message)

    def order_cancelled(self, receiver: str, order: Order):
        if not isinstance(receiver, str):
            raise TypeError("receiver should be a string")

        if not isinstance(order, Order):
            raise TypeError("order should be an instance of Order class")

        if receiver.strip() == "":
            raise ValueError("receiver shouldn't be empty")

        message = (
            f"Order ID {order.order_id} has been successfully cancelled "
            f"with total {order.calculate_total()} ..."
        )

        self.notification.send_notification(receiver, message)

    def order_completed(self, receiver: str, order: Order):
        if not isinstance(receiver, str):
            raise TypeError("receiver should be a string")

        if not isinstance(order, Order):
            raise TypeError("order should be an instance of Order class")

        if receiver.strip() == "":
            raise ValueError("receiver shouldn't be empty")

        message = (
            f"Order ID {order.order_id} has been successfully completed "
            f"with total {order.calculate_total()} ..."
        )

        self.notification.send_notification(receiver, message)


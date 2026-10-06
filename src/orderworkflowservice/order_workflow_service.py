from services.inventory_reserve_service import InventoryService
from repository.payment_protocol import Payment, PaymentService
from repository.notification_prorocol import EmailNotification, NotificationService
from uuid import UUID
from cart.cart_model import Cart
from repository.payment_protocol import PaymentMStatus, PaymentProcessor
from order.order_model_module import Order
from services.checkout_service import CheckoutService
from services.order_service import OrderService
from exceptions.exceptions_modules import UnexpectedPaymentStatusError


class OrderWorkflowService:
    def __init__(
        self,
        check_out_service: CheckoutService,
        inventory_service: InventoryService,
        payment_service: PaymentService,
        notification_service: NotificationService,
        order_service: OrderService,
    ) -> None:
        self.check_out_service = check_out_service
        self.inventory_service = inventory_service
        self.payment_service = payment_service
        self.notification_service = notification_service
        self.order_service = order_service

    def place_order(
        self, customer_id: UUID, cart: Cart, payment_method: PaymentProcessor
    ) -> tuple[Order, Payment]:
        order: Order = self.check_out_service.checkout(customer_id, cart)
        customer = order.customer
        amount = order.calculate_total()

        payment_ser = self.payment_service.process_payment(
            payment_method, amount, customer, order
        )
        if payment_ser.status == PaymentMStatus.SUCCESS:

            self.order_service.confirm_order(order.order_id)
            self.notification_service.make_notification(
                customer.name,
                f"order {order.order_id} with total {amount} has been completed successfully .. ",
            )
        elif payment_ser.status == PaymentMStatus.FAILED:
            self.order_service.cancel_order(order.order_id)

            self.notification_service.make_notification(
                customer.name,
                f"order {order.order_id} with total {amount} has been rejected",
            )
        else:
            self.order_service.cancel_order(order.order_id)
            raise UnexpectedPaymentStatusError("Something happened")

        return (order, payment_ser)

from services.checkout_service import CheckoutService
from services.inventory_reserve_service import InventoryService
from repository.payment_protocol import PaymentService
from src.repository.notification_prorocol import EmailNotification, NotificationService
from uuid import UUID
from src.cart.cart_model import Cart
from src.repository.payment_protocol import PaymentMStatus, PaymentProcessor
from src.order.order_model_module import Order
from src.services.checkout_service import CheckoutService
from src.services.customer_service import CustomerService


class OrderWorkflowService:
    def __init__(
        self,
        check_out_service: CheckoutService,
        inventory_service: InventoryService,
        payment_service: PaymentService,
        notification_service: NotificationService,
    ) -> None:
        self.check_out_service = check_out_service
        self.inventory_service = inventory_service
        self.payment_service = payment_service
        self.notification_service = notification_service

    def place_order(
        self, customer_id: UUID, cart: Cart, payment_method: PaymentProcessor
    ):
        order: Order = self.check_out_service.checkout(customer_id, cart)
        customer = order.customer
        amount = order.calculate_total()

        payment_ser = self.payment_service.process_payment(
            payment_method, amount, customer, order
        )
        if payment_ser.status == PaymentMStatus.SUCCESS:
            order.confirm_order()
            notification = EmailNotification()
            self.notification_service.make_notification(
                customer.name,
                f"order {order.order_id} with total {order.calculate_total()} has been completed successfully .. ",
            )
            print("successfully")
        elif payment_ser.status == PaymentMStatus.FAILED:
            for item in cart.items:
                self.inventory_service.release_stock(
                    item.get("product_id"), item.get("product_quantity")
                )
                notification = EmailNotification()
                self.notification_service.make_notification(
                    customer.name,
                    f"order {order.order_id} with total {order.calculate_total()} has been rejected",
                )

            print("unsuccessfully")

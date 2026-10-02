class ECommerceException(Exception):
    pass


class InsufficientStockAmount(ECommerceException):
    pass


class ItemNotFoundError(ECommerceException):
    pass


class InvalidProductStatusError(ECommerceException):
    pass


class OrderStatusError(ECommerceException):
    pass


class ProductNotFoundError(ECommerceException):
    pass


class ProductAddToCartError(ECommerceException):
    pass


class ProductNotAddedToCartError(ECommerceException):
    pass


class CustomerNotFoundError(ECommerceException):
    pass


class ProductNotAvailableError(ECommerceException):
    pass


class OrderCantBeCancalledError(ECommerceException):
    pass


class OrderCantBeConfirmedError(ECommerceException):
    pass

class ItemReserveError(ECommerceException):
    pass
class UnexpectedPaymentStatusError(ECommerceException):
    pass

from unittest.mock import Mock
import pytest

from repository.notification_prorocol import NotificationService, SmsNotification


def test_notification_service_calls_send_notification():
    fake_notification = Mock()  # بدل SmsNotification/EmailNotification الحقيقية
    service = NotificationService(notification=fake_notification)

    service.make_notification("0501234567", "Order confirmed")

    fake_notification.send_notification.assert_called_once_with(
        "0501234567", "Order confirmed"
    )


def test_notification_service_calls_send_notification_sms():
    fake_notification_sms = Mock()
    service_notification = NotificationService(notification=fake_notification_sms)
    service_notification.make_notification("basheer", "hi from test")

    fake_notification_sms.send_notification.assert_called_once_with(
        "basheer", "hi from test"
    )


def test_make_notification_invalid_receiver_type_raises():
    notification = SmsNotification()
    service_notification = NotificationService(notification=notification)
    with pytest.raises(TypeError):
        service_notification.make_notification(123, "hi from test")
        
        
def test_make_notification_empty_message_raises():
    notification = SmsNotification()
    service_notification = NotificationService(notification=notification)
    with pytest.raises(ValueError):
        service_notification.make_notification("", "hi from test")

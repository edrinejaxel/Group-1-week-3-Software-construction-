import pytest
from uuid import uuid4
from datetime import datetime

from application.services.notification_service import NotificationService
from infrastructure.adapters.notification_adapter import MockNotificationAdapter
from domain.entities.transaction import Transaction, TransactionType

@pytest.fixture
def notification_adapter():
    return MockNotificationAdapter()

@pytest.fixture
def notification_service(notification_adapter):
    return NotificationService(notification_adapter)

def test_notify_deposit(notification_service):
    transaction = Transaction(
        transaction_id=uuid4(),
        account_id=uuid4(),
        transaction_type=TransactionType.DEPOSIT,
        amount=100.0,
        timestamp=datetime.utcnow()
    )
    notification_service.notify(transaction)
    # Mock adapter logs to console, no assertion needed

def test_notify_transfer(notification_service):
    transaction = Transaction(
        transaction_id=uuid4(),
        account_id=uuid4(),
        transaction_type=TransactionType.TRANSFER,
        amount=50.0,
        timestamp=datetime.utcnow(),
        destination_account_id=uuid4()
    )
    notification_service.notify(transaction)
    # Mock adapter logs to console, no assertion needed
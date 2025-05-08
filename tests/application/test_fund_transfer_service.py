import pytest
from uuid import UUID, uuid4
from datetime import datetime, timedelta

from domain.entities.account import Account, AccountType, AccountStatus
from domain.entities.transaction import Transaction
from domain.services.limit_constraint import LimitConstraint
from domain.exceptions.domain_exceptions import (
    InsufficientFundsError,
    AccountNotFoundError,
    TransactionLimitExceededError,
)
from infrastructure.repositories.account_repository import InMemoryAccountRepository
from infrastructure.repositories.transaction_repository import InMemoryTransactionRepository

@pytest.fixture
def account_repository():
    return InMemoryAccountRepository()

@pytest.fixture
def transaction_repository():
    return InMemoryTransactionRepository()

@pytest.fixture
def source_account(account_repository):
    account = Account(
        account_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
        account_type=AccountType.CHECKING,
        balance=200.0,
        status=AccountStatus.ACTIVE,
        creation_date=datetime.utcnow(),
    )
    account_repository.create_account(account)
    return account

@pytest.fixture
def destination_account(account_repository):
    account = Account(
        account_id=UUID("123e4567-e89b-12d3-a456-426614174001"),
        account_type=AccountType.CHECKING,
        balance=100.0,
        status=AccountStatus.ACTIVE,
        creation_date=datetime.utcnow(),
    )
    account_repository.create_account(account)
    return account

@pytest.fixture
def fund_transfer_service(account_repository, transaction_repository):
    from application.services.notification_service import NotificationService
    from infrastructure.adapters.notification_adapter import MockNotificationAdapter
    notification_service = NotificationService(MockNotificationAdapter())
    from application.services.fund_transfer_service import FundTransferService
    return FundTransferService(account_repository, transaction_repository, notification_service)

def test_transfer_success(fund_transfer_service, source_account, destination_account, transaction_repository, account_repository):
    amount = 50.0
    transaction = fund_transfer_service.transfer_funds(
        source_account.account_id,
        destination_account.account_id,
        amount
    )
    updated_source = account_repository.get_account_by_id(source_account.account_id)
    updated_destination = account_repository.get_account_by_id(destination_account.account_id)
    transactions = transaction_repository.get_transactions_for_account(source_account.account_id)
    assert updated_source.balance == 150.0
    assert updated_destination.balance == 150.0
    assert len(transactions) == 1
    assert transactions[0].amount == amount
    assert transaction.transaction_id == transactions[0].transaction_id

def test_transfer_insufficient_funds(fund_transfer_service, source_account, destination_account):
    with pytest.raises(InsufficientFundsError):
        fund_transfer_service.transfer_funds(
            source_account.account_id,
            destination_account.account_id,
            300.0
        )

def test_transfer_with_limits(fund_transfer_service, source_account, destination_account, account_repository):
    source_account.limit_constraint = LimitConstraint(daily_limit=100.0, monthly_limit=500.0)
    source_account.daily_spent = 80.0
    account_repository.update_account(source_account)
    with pytest.raises(TransactionLimitExceededError):
        fund_transfer_service.transfer_funds(
            source_account.account_id,
            destination_account.account_id,
            50.0
        )
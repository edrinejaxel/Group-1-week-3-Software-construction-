import pytest
from uuid import UUID, uuid4
from datetime import datetime

from domain.entities.account import Account, AccountType, AccountStatus
from domain.entities.transaction import Transaction, TransactionType
from domain.exceptions.domain_exceptions import (
    InsufficientFundsError,
    InvalidAmountError,
    AccountNotFoundError,
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
def notification_service():
    from infrastructure.adapters.notification_adapter import MockNotificationAdapter
    from application.services.notification_service import NotificationService
    return NotificationService(MockNotificationAdapter())

@pytest.fixture
def account_id(account_repository):
    account = Account(
        account_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
        account_type=AccountType.CHECKING,
        balance=100.0,
        status=AccountStatus.ACTIVE,
        creation_date=datetime.utcnow(),
    )
    account_repository.create_account(account)
    return account.account_id

@pytest.fixture
def transaction_service(account_repository, transaction_repository, notification_service):
    from application.services.transaction_service import TransactionService
    return TransactionService(account_repository, transaction_repository, notification_service)

def test_deposit_success(transaction_service, account_repository, account_id, transaction_repository):
    amount = 50.0
    transaction = transaction_service.deposit(account_id, amount)
    updated_account = account_repository.get_account_by_id(account_id)
    transactions = transaction_repository.get_transactions_for_account(account_id)
    assert updated_account.balance == 150.0
    assert len(transactions) == 1
    assert transactions[0].amount == amount

def test_withdraw_success(transaction_service, account_repository, account_id, transaction_repository):
    amount = 30.0
    transaction = transaction_service.withdraw(account_id, amount)
    updated_account = account_repository.get_account_by_id(account_id)
    transactions = transaction_repository.get_transactions_for_account(account_id)
    assert updated_account.balance == 70.0
    assert len(transactions) == 1
    assert transactions[0].amount == amount

def test_withdraw_insufficient_funds(transaction_service, account_id):
    with pytest.raises(InsufficientFundsError):
        transaction_service.withdraw(account_id, 200.0)

def test_withdraw_negative_amount(transaction_service, account_id):
    with pytest.raises(InvalidAmountError):
        transaction_service.withdraw(account_id, -10.0)

def test_deposit_account_not_found(transaction_service):
    with pytest.raises(AccountNotFoundError):
        transaction_service.deposit(uuid4(), 50.0)
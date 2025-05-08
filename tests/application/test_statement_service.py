import pytest
from uuid import UUID, uuid4
from datetime import datetime, timedelta

from domain.entities.account import Account, AccountType, AccountStatus
from domain.entities.transaction import Transaction, TransactionType
from infrastructure.repositories.account_repository import InMemoryAccountRepository
from infrastructure.repositories.transaction_repository import InMemoryTransactionRepository
from infrastructure.adapters.statement_adapter import MockStatementAdapter

@pytest.fixture
def account_repository():
    return InMemoryAccountRepository()

@pytest.fixture
def transaction_repository():
    return InMemoryTransactionRepository()

@pytest.fixture
def statement_adapter():
    return MockStatementAdapter()

@pytest.fixture
def account(account_repository):
    account = Account(
        account_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
        account_type=AccountType.CHECKING,
        balance=1000.0,
        status=AccountStatus.ACTIVE,
        creation_date=datetime.utcnow(),
    )
    account_repository.create_account(account)
    return account

@pytest.fixture
def statement_service(account_repository, transaction_repository, statement_adapter):
    from application.services.statement_service import StatementService
    return StatementService(account_repository, transaction_repository, statement_adapter)

def test_generate_statement_success(statement_service, account, transaction_repository):
    transaction = Transaction(
        transaction_id=uuid4(),
        account_id=account.account_id,
        transaction_type=TransactionType.DEPOSIT,
        amount=100.0,
        timestamp=datetime.utcnow(),
        destination_account_id=None
    )
    transaction_repository.save_transaction(transaction)
    start_date = datetime.utcnow() - timedelta(days=30)
    end_date = datetime.utcnow()
    statement = statement_service.generate_statement(account.account_id, start_date, end_date)
    assert len(statement.transactions) == 1
    assert statement.transactions[0].amount == 100.0

def test_generate_statement_account_not_found(statement_service):
    start_date = datetime.utcnow() - timedelta(days=30)
    end_date = datetime.utcnow()
    with pytest.raises(Exception):  # Replace with specific exception if defined
        statement_service.generate_statement(uuid4(), start_date, end_date)
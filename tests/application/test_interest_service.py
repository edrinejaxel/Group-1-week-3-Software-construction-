import pytest
from uuid import UUID, uuid4
from datetime import datetime

from domain.entities.account import Account, AccountType, AccountStatus
from domain.services.interest_strategy import SavingsInterestStrategy
from domain.exceptions.domain_exceptions import AccountNotFoundError
from infrastructure.repositories.account_repository import InMemoryAccountRepository

@pytest.fixture
def account_repository():
    return InMemoryAccountRepository()

@pytest.fixture
def notification_service():
    from infrastructure.adapters.notification_adapter import MockNotificationAdapter
    from application.services.notification_service import NotificationService
    return NotificationService(MockNotificationAdapter())

@pytest.fixture
def account(account_repository):
    account = Account(
        account_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
        account_type=AccountType.SAVINGS,
        balance=1000.0,
        status=AccountStatus.ACTIVE,
        creation_date=datetime.utcnow(),
        interest_strategy=SavingsInterestStrategy()
    )
    account_repository.create_account(account)
    return account

@pytest.fixture
def interest_service(account_repository, notification_service):
    from application.services.interest_service import InterestService
    return InterestService(account_repository, notification_service)

def test_apply_interest_success(interest_service, account_repository, account):
    interest = interest_service.apply_interest_to_account(account.account_id)
    updated_account = account_repository.get_account_by_id(account.account_id)
    assert interest == 30.0
    assert updated_account.balance == 1030.0

def test_apply_interest_account_not_found(interest_service):
    with pytest.raises(AccountNotFoundError):
        interest_service.apply_interest_to_account(uuid4())
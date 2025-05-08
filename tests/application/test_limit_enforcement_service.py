import pytest
from uuid import uuid4, UUID
from datetime import datetime, timedelta

from domain.entities.account import Account, AccountType
from domain.services.limit_constraint import LimitConstraint
from infrastructure.repositories.account_repository import InMemoryAccountRepository

@pytest.fixture
def account_repository():
    return InMemoryAccountRepository()

@pytest.fixture
def account(account_repository):
    account = Account.create(AccountType.CHECKING, initial_deposit=1000.0)
    account_repository.create_account(account)
    return account

@pytest.fixture
def limit_enforcement_service(account_repository):
    from application.services.limit_enforcement_service import LimitEnforcementService
    return LimitEnforcementService(account_repository)

def test_set_limits_success(limit_enforcement_service, account_repository, account):
    limit_enforcement_service.set_limits(account.account_id, daily_limit=100.0, monthly_limit=500.0)
    updated_account = account_repository.get_account_by_id(account.account_id)
    assert updated_account.limit_constraint.daily_limit == 100.0
    assert updated_account.limit_constraint.monthly_limit == 500.0

def test_set_limits_account_not_found(limit_enforcement_service):
    with pytest.raises(Exception):  # Replace with specific exception if defined
        limit_enforcement_service.set_limits(uuid4(), 100.0, 500.0)

def test_reset_limits(limit_enforcement_service, account_repository, account):
    account.daily_spent = 50.0
    account.monthly_spent = 200.0
    account_repository.update_account(account)
    next_day = datetime.utcnow() + timedelta(days=1)
    limit_enforcement_service.reset_limits(account.account_id)
    updated_account = account_repository.get_account_by_id(account.account_id)
    assert updated_account.daily_spent == 0.0  # Reset for next day
    assert updated_account.monthly_spent == 0.0  # Reset for next month
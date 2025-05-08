import pytest
from uuid import UUID

from application.services.account_creation_service import AccountCreationService
from infrastructure.repositories.account_repository import InMemoryAccountRepository
from domain.exceptions.domain_exceptions import InvalidAmountError
from domain.services.interest_strategy import SavingsInterestStrategy

@pytest.fixture
def account_repository():
    return InMemoryAccountRepository()

@pytest.fixture
def account_creation_service(account_repository):
    return AccountCreationService(account_repository)

def test_create_checking_account(account_creation_service, account_repository):
    account_id = account_creation_service.create_account("CHECKING", initial_deposit=100.0)
    account = account_repository.get_account_by_id(account_id)
    assert isinstance(account_id, UUID)
    assert account.account_type.value == "CHECKING"
    assert account.balance == 100.0
    assert account.interest_strategy is not None

def test_create_savings_account(account_creation_service, account_repository):
    account_id = account_creation_service.create_account("SAVINGS", initial_deposit=100.0)
    account = account_repository.get_account_by_id(account_id)
    assert isinstance(account_id, UUID)
    assert account.account_type.value == "SAVINGS"
    assert isinstance(account.interest_strategy, SavingsInterestStrategy)

def test_create_account_with_negative_deposit(account_creation_service):
    with pytest.raises(InvalidAmountError):
        account_creation_service.create_account("SAVINGS", initial_deposit=-50.0)

def test_create_account_invalid_type(account_creation_service):
    with pytest.raises(ValueError):
        account_creation_service.create_account("INVALID")
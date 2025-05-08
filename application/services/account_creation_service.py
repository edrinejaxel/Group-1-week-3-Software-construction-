from uuid import UUID

from domain.entities.account import Account, AccountType
from domain.exceptions.domain_exceptions import InvalidAmountError
from infrastructure.repositories.account_repository import AccountRepository
from domain.services.interest_strategy import CheckingInterestStrategy, SavingsInterestStrategy

class AccountCreationService:
    def __init__(self, account_repository: AccountRepository):
        self.account_repository = account_repository

    def create_account(self, account_type: str, initial_deposit: float = 0.0) -> UUID:
        try:
            account_type_enum = AccountType(account_type.upper())
        except ValueError:
            raise ValueError(f"Invalid account type: {account_type}")

        if initial_deposit < 0:
            raise InvalidAmountError("Initial deposit cannot be negative")

        interest_strategy = (
            SavingsInterestStrategy() if account_type_enum == AccountType.SAVINGS
            else CheckingInterestStrategy()
        )
        account = Account.create(account_type_enum, initial_deposit)
        account.interest_strategy = interest_strategy
        self.account_repository.create_account(account)
        return account.account_id
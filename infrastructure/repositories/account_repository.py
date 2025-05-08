from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from domain.entities.account import Account

class AccountRepository(ABC):
    @abstractmethod
    def get_account_by_id(self, account_id: UUID) -> Optional[Account]:
        pass

    @abstractmethod
    def update_account(self, account: Account) -> None:
        pass

    @abstractmethod
    def create_account(self, account: Account) -> None:
        pass

class InMemoryAccountRepository(AccountRepository):
    def __init__(self):
        self.accounts: dict[UUID, Account] = {}

    def get_account_by_id(self, account_id: UUID) -> Optional[Account]:
        return self.accounts.get(account_id)

    def update_account(self, account: Account) -> None:
        if account.account_id in self.accounts:
            self.accounts[account.account_id] = account

    def create_account(self, account: Account) -> None:
        self.accounts[account.account_id] = account
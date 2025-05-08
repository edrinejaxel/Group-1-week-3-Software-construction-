from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from domain.entities.transaction import Transaction

class TransactionRepository(ABC):
    @abstractmethod
    def get_transactions_for_account(self, account_id: UUID) -> List[Transaction]:
        pass

    @abstractmethod
    def save_transaction(self, transaction: Transaction) -> None:
        pass

class InMemoryTransactionRepository(TransactionRepository):
    def __init__(self):
        self.transactions: dict[UUID, List[Transaction]] = {}

    def get_transactions_for_account(self, account_id: UUID) -> List[Transaction]:
        return self.transactions.get(account_id, [])

    def save_transaction(self, transaction: Transaction) -> None:
        if transaction.account_id not in self.transactions:
            self.transactions[transaction.account_id] = []
        self.transactions[transaction.account_id].append(transaction)
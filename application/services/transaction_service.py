from uuid import UUID
from datetime import datetime

from domain.entities.account import Account
from domain.entities.transaction import Transaction
from domain.exceptions.domain_exceptions import AccountNotFoundError
from infrastructure.repositories.account_repository import AccountRepository
from infrastructure.repositories.transaction_repository import TransactionRepository
from application.services.notification_service import NotificationService

class TransactionService:
    def __init__(
        self,
        account_repository: AccountRepository,
        transaction_repository: TransactionRepository,
        notification_service: NotificationService,
    ):
        self.account_repository = account_repository
        self.transaction_repository = transaction_repository
        self.notification_service = notification_service

    def deposit(self, account_id: UUID, amount: float) -> Transaction:
        account = self.account_repository.get_account_by_id(account_id)
        if not account:
            raise AccountNotFoundError(f"Account {account_id} not found")

        account.deposit(amount)
        transaction = Transaction.create_deposit(account_id, amount)
        self.account_repository.update_account(account)
        self.transaction_repository.save_transaction(transaction)
        self.notification_service.notify(transaction)
        return transaction

    def withdraw(self, account_id: UUID, amount: float) -> Transaction:
        account = self.account_repository.get_account_by_id(account_id)
        if not account:
            raise AccountNotFoundError(f"Account {account_id} not found")

        account.reset_limits(datetime.utcnow())
        account.withdraw(amount)
        transaction = Transaction.create_withdrawal(account_id, amount)
        self.account_repository.update_account(account)
        self.transaction_repository.save_transaction(transaction)
        self.notification_service.notify(transaction)
        return transaction
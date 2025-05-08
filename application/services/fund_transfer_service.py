from uuid import UUID
from datetime import datetime

from domain.entities.transaction import Transaction
from domain.exceptions.domain_exceptions import AccountNotFoundError
from infrastructure.repositories.account_repository import AccountRepository
from infrastructure.repositories.transaction_repository import TransactionRepository
from application.services.notification_service import NotificationService

class FundTransferService:
    def __init__(
        self,
        account_repository: AccountRepository,
        transaction_repository: TransactionRepository,
        notification_service: NotificationService,
    ):
        self.account_repository = account_repository
        self.transaction_repository = transaction_repository
        self.notification_service = notification_service

    def transfer_funds(
        self,
        source_account_id: UUID,
        destination_account_id: UUID,
        amount: float
    ) -> Transaction:
        source_account = self.account_repository.get_account_by_id(source_account_id)
        destination_account = self.account_repository.get_account_by_id(destination_account_id)
        if not source_account:
            raise AccountNotFoundError(f"Source account {source_account_id} not found")
        if not destination_account:
            raise AccountNotFoundError(f"Destination account {destination_account_id} not found")

        source_account.reset_limits(datetime.utcnow())
        destination_account.reset_limits(datetime.utcnow())
        source_account.withdraw(amount)
        destination_account.deposit(amount)
        transaction = Transaction.create_transfer(source_account_id, destination_account_id, amount)
        self.account_repository.update_account(source_account)
        self.account_repository.update_account(destination_account)
        self.transaction_repository.save_transaction(transaction)
        self.notification_service.notify(transaction)
        return transaction
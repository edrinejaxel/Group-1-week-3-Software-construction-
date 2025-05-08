from uuid import UUID, uuid4
from datetime import datetime

from domain.exceptions.domain_exceptions import AccountNotFoundError
from domain.entities.transaction import Transaction, TransactionType
from infrastructure.repositories.account_repository import AccountRepository
from application.services.notification_service import NotificationService

class InterestService:
    def __init__(
        self,
        account_repository: AccountRepository,
        notification_service: NotificationService
    ):
        self.account_repository = account_repository
        self.notification_service = notification_service

    def apply_interest_to_account(self, account_id: UUID) -> float:
        account = self.account_repository.get_account_by_id(account_id)
        if not account:
            raise AccountNotFoundError(f"Account {account_id} not found")

        interest = account.apply_interest()
        if interest > 0:
            self.account_repository.update_account(account)
            # Create a transaction for interest
            transaction = Transaction(
                transaction_id=uuid4(),
                account_id=account_id,
                transaction_type=TransactionType.DEPOSIT,
                amount=interest,
                timestamp=datetime.utcnow(),
                destination_account_id=None
            )
            self.notification_service.notify(transaction)
        return interest
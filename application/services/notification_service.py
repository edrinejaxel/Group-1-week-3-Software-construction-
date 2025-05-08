from domain.entities.transaction import Transaction
from infrastructure.adapters.notification_adapter import NotificationAdapter

class NotificationService:
    def __init__(self, notification_adapter: NotificationAdapter):
        self.notification_adapter = notification_adapter

    def notify(self, transaction: Transaction) -> None:
        message = (
            f"Transaction {transaction.transaction_type.value} of {transaction.amount} "
            f"on account {transaction.account_id}"
        )
        if transaction.destination_account_id:
            message += f" to account {transaction.destination_account_id}"
        self.notification_adapter.send_notification(
            recipient=f"user_{transaction.account_id}@example.com",
            message=message
        )
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4
from typing import Optional

class TransactionType(Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"
    TRANSFER = "TRANSFER"

@dataclass
class Transaction:
    transaction_id: UUID
    account_id: UUID
    transaction_type: TransactionType
    amount: float
    timestamp: datetime
    destination_account_id: Optional[UUID] = None

    @staticmethod
    def create_deposit(account_id: UUID, amount: float) -> "Transaction":
        return Transaction(
            transaction_id=uuid4(),
            account_id=account_id,
            transaction_type=TransactionType.DEPOSIT,
            amount=amount,
            timestamp=datetime.utcnow(),
        )

    @staticmethod
    def create_withdrawal(account_id: UUID, amount: float) -> "Transaction":
        return Transaction(
            transaction_id=uuid4(),
            account_id=account_id,
            transaction_type=TransactionType.WITHDRAW,
            amount=amount,
            timestamp=datetime.utcnow(),
        )

    @staticmethod
    def create_transfer(
        source_account_id: UUID,
        destination_account_id: UUID,
        amount: float
    ) -> "Transaction":
        return Transaction(
            transaction_id=uuid4(),
            account_id=source_account_id,
            transaction_type=TransactionType.TRANSFER,
            amount=amount,
            timestamp=datetime.utcnow(),
            destination_account_id=destination_account_id,
        )
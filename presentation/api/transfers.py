from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from pydantic import BaseModel
from application.services.fund_transfer_service import FundTransferService
from infrastructure.repositories.account_repository import InMemoryAccountRepository
from infrastructure.repositories.transaction_repository import InMemoryTransactionRepository
from infrastructure.adapters.notification_adapter import MockNotificationAdapter
from application.services.notification_service import NotificationService
from domain.exceptions.domain_exceptions import AccountNotFoundError, InsufficientFundsError, TransactionLimitExceededError

router = APIRouter()

# Initialize repositories and services
account_repository = InMemoryAccountRepository()
transaction_repository = InMemoryTransactionRepository()
notification_service = NotificationService(MockNotificationAdapter())
fund_transfer_service = FundTransferService(account_repository, transaction_repository, notification_service)

class TransferRequest(BaseModel):
    source_account_id: UUID
    destination_account_id: UUID
    amount: float

@router.post("/", response_model=dict)
async def transfer_funds(transfer: TransferRequest):
    try:
        transaction = fund_transfer_service.transfer_funds(
            transfer.source_account_id,
            transfer.destination_account_id,
            transfer.amount
        )
        return {"transaction_id": transaction.transaction_id}
    except AccountNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except (InsufficientFundsError, TransactionLimitExceededError) as e:
        raise HTTPException(status_code=400, detail=str(e))
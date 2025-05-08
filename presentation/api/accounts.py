from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Literal
from datetime import date

from application.services.account_creation_service import AccountCreationService
from application.services.transaction_service import TransactionService
from application.services.fund_transfer_service import FundTransferService
from application.services.interest_service import InterestService
from application.services.limit_enforcement_service import LimitEnforcementService
from application.services.notification_service import NotificationService
from domain.exceptions.domain_exceptions import (
    InsufficientFundsError,
    InvalidAmountError,
    InvalidAccountStatusError,
    AccountNotFoundError,
    TransactionLimitExceededError,
)
from infrastructure.repositories.account_repository import InMemoryAccountRepository
from infrastructure.repositories.transaction_repository import InMemoryTransactionRepository
from infrastructure.adapters.notification_adapter import MockNotificationAdapter
from infrastructure.adapters.logging_adapter import LoggingAdapter

router = APIRouter()

# Dependency injection
account_repo = InMemoryAccountRepository()
transaction_repo = InMemoryTransactionRepository()
notification_adapter = MockNotificationAdapter()
logging_adapter = LoggingAdapter()
notification_service = logging_adapter.log_method(NotificationService(notification_adapter))
account_creation_service = logging_adapter.log_method(AccountCreationService(account_repo))
transaction_service = logging_adapter.log_method(TransactionService(account_repo, transaction_repo, notification_service))
fund_transfer_service = logging_adapter.log_method(FundTransferService(account_repo, transaction_repo, notification_service))
interest_service = logging_adapter.log_method(InterestService(account_repo, notification_service))
limit_enforcement_service = logging_adapter.log_method(LimitEnforcementService(account_repo))

# Pydantic models
class CreateAccountRequest(BaseModel):
    account_type: Literal["CHECKING", "SAVINGS"]
    initial_deposit: float = Field(default=0.0, ge=0.0)

class TransactionRequest(BaseModel):
    amount: float = Field(gt=0.0)

class TransferRequest(BaseModel):
    source_account_id: UUID
    destination_account_id: UUID
    amount: float = Field(gt=0.0)

class LimitRequest(BaseModel):
    daily_limit: float = Field(ge=0.0)
    monthly_limit: float = Field(ge=0.0)

class InterestRequest(BaseModel):
    calculation_date: date

class AccountResponse(BaseModel):
    account_id: UUID
    account_type: str
    balance: float
    status: str
    creation_date: str

class TransactionResponse(BaseModel):
    transaction_id: UUID
    account_id: UUID
    transaction_type: str
    amount: float
    timestamp: str
    destination_account_id: UUID | None

class LimitResponse(BaseModel):
    daily_limit: float
    monthly_limit: float
    daily_spent: float
    monthly_spent: float

@router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(request: CreateAccountRequest):
    try:
        account_id = account_creation_service.create_account(
            request.account_type, request.initial_deposit
        )
        account = account_repo.get_account_by_id(account_id)
        return AccountResponse(
            account_id=account.account_id,
            account_type=account.account_type.value,
            balance=account.balance,
            status=account.status.value,
            creation_date=account.creation_date.isoformat(),
        )
    except (ValueError, InvalidAmountError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{account_id}/deposit", response_model=TransactionResponse)
async def deposit(account_id: UUID, request: TransactionRequest):
    try:
        transaction = transaction_service.deposit(account_id, request.amount)
        return TransactionResponse(
            transaction_id=transaction.transaction_id,
            account_id=transaction.account_id,
            transaction_type=transaction.transaction_type.value,
            amount=transaction.amount,
            timestamp=transaction.timestamp.isoformat(),
            destination_account_id=transaction.destination_account_id,
        )
    except (AccountNotFoundError, InvalidAmountError, InvalidAccountStatusError, TransactionLimitExceededError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{account_id}/withdraw", response_model=TransactionResponse)
async def withdraw(account_id: UUID, request: TransactionRequest):
    try:
        transaction = transaction_service.withdraw(account_id, request.amount)
        return TransactionResponse(
            transaction_id=transaction.transaction_id,
            account_id=transaction.account_id,
            transaction_type=transaction.transaction_type.value,
            amount=transaction.amount,
            timestamp=transaction.timestamp.isoformat(),
            destination_account_id=transaction.destination_account_id,
        )
    except (AccountNotFoundError, InvalidAmountError, InvalidAccountStatusError, InsufficientFundsError, TransactionLimitExceededError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/transfer", response_model=TransactionResponse)
async def transfer(request: TransferRequest):
    try:
        transaction = fund_transfer_service.transfer_funds(
            request.source_account_id,
            request.destination_account_id,
            request.amount
        )
        return TransactionResponse(
            transaction_id=transaction.transaction_id,
            account_id=transaction.account_id,
            transaction_type=transaction.transaction_type.value,
            amount=transaction.amount,
            timestamp=transaction.timestamp.isoformat(),
            destination_account_id=transaction.destination_account_id,
        )
    except (AccountNotFoundError, InvalidAmountError, InsufficientFundsError, TransactionLimitExceededError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{account_id}/interest/calculate")
async def calculate_interest(account_id: UUID, request: InterestRequest):
    try:
        interest = interest_service.apply_interest_to_account(account_id)
        return {"interest_applied": interest}
    except AccountNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.patch("/{account_id}/limits")
async def update_limits(account_id: UUID, request: LimitRequest):
    try:
        limit_enforcement_service.set_limits(
            account_id,
            request.daily_limit,
            request.monthly_limit
        )
        return {"message": "Limits updated successfully"}
    except AccountNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{account_id}/balance")
async def get_balance(account_id: UUID):
    account = account_repo.get_account_by_id(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"balance": account.balance, "available_balance": account.balance}

@router.get("/{account_id}/transactions", response_model=list[TransactionResponse])
async def get_transactions(account_id: UUID):
    transactions = transaction_repo.get_transactions_for_account(account_id)
    return [
        TransactionResponse(
            transaction_id=tx.transaction_id,
            account_id=tx.account_id,
            transaction_type=tx.transaction_type.value,
            amount=tx.amount,
            timestamp=tx.timestamp.isoformat(),
            destination_account_id=tx.destination_account_id,
        )
        for tx in transactions
    ]

@router.get("/{account_id}/limits", response_model=LimitResponse)
async def get_limits(account_id: UUID):
    account = account_repo.get_account_by_id(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    daily_limit = account.limit_constraint.daily_limit if account.limit_constraint else float('inf')
    monthly_limit = account.limit_constraint.monthly_limit if account.limit_constraint else float('inf')
    return LimitResponse(
        daily_limit=daily_limit,
        monthly_limit=monthly_limit,
        daily_spent=account.daily_spent,
        monthly_spent=account.monthly_spent
    )
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from domain.exceptions.domain_exceptions import (
    InsufficientFundsError,
    InvalidAmountError,
    InvalidAccountStatusError,
)
from domain.services.interest_strategy import InterestStrategy
from domain.services.limit_constraint import LimitConstraint

class AccountType(Enum):
    CHECKING = "CHECKING"
    SAVINGS = "SAVINGS"

class AccountStatus(Enum):
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"

@dataclass
class Account:
    account_id: UUID
    account_type: AccountType
    balance: float
    status: AccountStatus
    creation_date: datetime
    interest_strategy: Optional[InterestStrategy] = None
    limit_constraint: Optional[LimitConstraint] = None
    daily_spent: float = 0.0
    monthly_spent: float = 0.0
    last_reset_date: Optional[datetime] = None

    @staticmethod
    def create(account_type: AccountType, initial_deposit: float = 0.0) -> "Account":
        if initial_deposit < 0:
            raise InvalidAmountError("Initial deposit cannot be negative")
        return Account(
            account_id=uuid4(),
            account_type=account_type,
            balance=initial_deposit,
            status=AccountStatus.ACTIVE,
            creation_date=datetime.utcnow(),
            last_reset_date=datetime.utcnow(),
        )

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise InvalidAmountError("Deposit amount must be positive")
        if self.status != AccountStatus.ACTIVE:
            raise InvalidAccountStatusError("Cannot deposit to a closed account")
        if self.limit_constraint:
            self.limit_constraint.check_deposit(self, amount)
        self.balance += amount

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise InvalidAmountError("Withdrawal amount must be positive")
        if self.status != AccountStatus.ACTIVE:
            raise InvalidAccountStatusError("Cannot withdraw from a closed account")
        if self.balance < amount:
            raise InsufficientFundsError("Insufficient funds for withdrawal")
        if self.limit_constraint:
            self.limit_constraint.check_withdrawal(self, amount)
        self.balance -= amount
        self.daily_spent += amount
        self.monthly_spent += amount

    def apply_interest(self) -> float:
        if not self.interest_strategy or self.status != AccountStatus.ACTIVE:
            return 0.0
        interest = self.interest_strategy.calculate_interest(self.balance)
        self.balance += interest
        return interest

    def reset_limits(self, current_date: datetime) -> None:
        if not self.last_reset_date:
            self.last_reset_date = current_date
            return
        # Reset daily limits
        if current_date.date() > self.last_reset_date.date():
            self.daily_spent = 0.0
        # Reset monthly limits only if a full month has passed
        if (current_date.year > self.last_reset_date.year or
                (current_date.year == self.last_reset_date.year and
                 current_date.month > self.last_reset_date.month)):
            self.monthly_spent = 0.0
        self.last_reset_date = current_date
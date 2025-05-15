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
    minimum_balance: float = 0.0
    last_interest_posting_date: Optional[datetime] = None
    failed_attempts: int = 0
    is_locked: bool = False
    overdraft_limit: float = 0.0
    transaction_count: int = 0
    max_daily_transactions: int = 1000
    last_statement_date: Optional[datetime] = None

    @staticmethod
    def create(account_type: AccountType, initial_deposit: float = 0.0) -> "Account":
        if initial_deposit < 0:
            raise InvalidAmountError("Initial deposit cannot be negative")
        
        # Set account type specific rules
        minimum_balance = 0.0
        overdraft_limit = 0.0
        max_daily_transactions = 1000
        
        if account_type == AccountType.SAVINGS:
            minimum_balance = 100.0  # Minimum balance for savings
            if initial_deposit < minimum_balance:
                raise InvalidAmountError(f"Savings account requires minimum initial deposit of ${minimum_balance}")
        elif account_type == AccountType.CHECKING:
            minimum_balance = 50.0   # Minimum balance for checking
            overdraft_limit = 100.0  # Overdraft limit for checking
        
        return Account(
            account_id=uuid4(),
            account_type=account_type,
            balance=initial_deposit,
            status=AccountStatus.ACTIVE,
            creation_date=datetime.utcnow(),
            last_reset_date=datetime.utcnow(),
            last_interest_posting_date=datetime.utcnow(),
            minimum_balance=minimum_balance,
            overdraft_limit=overdraft_limit,
            max_daily_transactions=max_daily_transactions
        )

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise InvalidAmountError("Deposit amount must be positive")
        if self.status != AccountStatus.ACTIVE:
            raise InvalidAccountStatusError("Cannot deposit to a closed account")
        if self.limit_constraint:
            self.limit_constraint.check_deposit(self, amount)
        self.balance += amount

    def validate_transaction(self) -> None:
        if self.is_locked:
            raise AccountLockedError("Account is temporarily locked")
        
        if self.transaction_count >= self.max_daily_transactions:
            raise TransactionLimitError("Daily transaction limit exceeded")
        
        if self.status != AccountStatus.ACTIVE:
            raise InvalidAccountStatusError("Account is not active")

    def withdraw(self, amount: float) -> None:
        self.validate_transaction()
        
        if amount <= 0:
            raise InvalidAmountError("Withdrawal amount must be positive")
            
        available_balance = self.balance + self.overdraft_limit
        if self.account_type == AccountType.SAVINGS:
            if self.balance - amount < self.minimum_balance:
                raise InsufficientFundsError(f"Cannot go below minimum balance of ${self.minimum_balance}")
        elif amount > available_balance:
            raise InsufficientFundsError("Insufficient funds including overdraft limit")
        
        if self.limit_constraint:
            self.limit_constraint.check_withdrawal(self, amount)
            
        self.balance -= amount
        self.daily_spent += amount
        self.monthly_spent += amount
        self.transaction_count += 1

    def apply_interest(self) -> float:
        if not self.interest_strategy or self.status != AccountStatus.ACTIVE:
            return 0.0
        interest = self.interest_strategy.calculate_interest(self.balance)
        self.balance += interest
        return interest

    def calculate_compound_interest(self) -> float:
        if not self.interest_strategy or self.status != AccountStatus.ACTIVE:
            return 0.0
            
        if not self.last_interest_posting_date:
            self.last_interest_posting_date = datetime.utcnow()
            return 0.0
            
        # Calculate days since last interest posting
        days = (datetime.utcnow() - self.last_interest_posting_date).days
        if days < 1:
            return 0.0
            
        # Calculate daily interest rate (APR/365)
        daily_rate = self.interest_strategy.calculate_interest(1.0) / 365
        
        # Calculate compound interest
        compound_interest = self.balance * ((1 + daily_rate) ** days - 1)
        
        # Update balance and last posting date
        self.balance += compound_interest
        self.last_interest_posting_date = datetime.utcnow()
        
        return compound_interest

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

    def increment_failed_attempts(self) -> None:
        self.failed_attempts += 1
        if self.failed_attempts >= 3:
            self.is_locked = True
            raise AccountLockedError("Account locked due to multiple failed attempts")

    def reset_security_status(self) -> None:
        self.failed_attempts = 0
        self.is_locked = False
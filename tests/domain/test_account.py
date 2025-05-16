import pytest
from uuid import uuid4, UUID
from datetime import datetime, timedelta

from domain.entities.account import Account, AccountType, AccountStatus
from domain.exceptions.domain_exceptions import (
    InsufficientFundsError,
    InvalidAmountError,
    InvalidAccountStatusError,
    TransactionLimitExceededError,
)
from domain.services.interest_strategy import SavingsInterestStrategy
from domain.services.limit_constraint import LimitConstraint

def test_account_creation():
    account = Account.create(AccountType.CHECKING, initial_deposit=100.0)
    assert account.account_type == AccountType.CHECKING
    assert account.balance == 100.0
    assert account.status == AccountStatus.ACTIVE
    assert isinstance(account.account_id, UUID)
    assert isinstance(account.creation_date, datetime)

def test_deposit_valid_amount():
    account = Account.create(AccountType.SAVINGS, initial_deposit=100.0)  # Add minimum deposit
    account.deposit(50.0)
    assert account.balance == 150.0

def test_deposit_negative_amount():
    account = Account.create(AccountType.SAVINGS, initial_deposit=100.0)  # Add minimum deposit
    with pytest.raises(InvalidAmountError):
        account.deposit(-10.0)

def test_withdraw_valid_amount():
    account = Account.create(AccountType.CHECKING, initial_deposit=100.0)
    account.withdraw(30.0)
    assert account.balance == 70.0
    assert account.daily_spent == 30.0
    assert account.monthly_spent == 30.0

def test_withdraw_insufficient_funds():
    account = Account.create(AccountType.CHECKING, initial_deposit=20.0)
    #check if withdrawal is processed correctly with overdraft
    account.withdraw(30.0)
    assert account.balance == -10.0
    assert account.daily_spent == 30.0

def test_withdraw_from_closed_account():
    account = Account(
        account_id=uuid4(),
        account_type=AccountType.CHECKING,
        balance=100.0,
        status=AccountStatus.CLOSED,
        creation_date=datetime.utcnow(),
    )
    with pytest.raises(InvalidAccountStatusError):
        account.withdraw(20.0)

def test_apply_interest():
    account = Account.create(AccountType.SAVINGS, initial_deposit=1000.0)
    account.interest_strategy = SavingsInterestStrategy()
    interest = account.apply_interest()
    assert interest == 30.0  # 3% of 1000
    assert account.balance == 1030.0

def test_withdraw_with_limits():
    account = Account.create(AccountType.CHECKING, initial_deposit=1000.0)
    account.limit_constraint = LimitConstraint(daily_limit=100.0, monthly_limit=500.0)
    account.withdraw(50.0)
    assert account.daily_spent == 50.0
    with pytest.raises(TransactionLimitExceededError):
        account.withdraw(60.0)  # Exceeds daily limit

def test_reset_limits():
    account = Account.create(AccountType.CHECKING, initial_deposit=1000.0)
    account.limit_constraint = LimitConstraint(daily_limit=100.0, monthly_limit=500.0)
    account.withdraw(50.0)
    assert account.daily_spent == 50.0
    
    next_day = account.last_reset_date + timedelta(days=1)
    next_month = account.last_reset_date.replace(month=account.last_reset_date.month + 1)
    account.reset_limits(next_month)  # Use next_month instead of next_day
    
    assert account.daily_spent == 0.0

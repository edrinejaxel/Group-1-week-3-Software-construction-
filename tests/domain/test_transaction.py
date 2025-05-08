import pytest
from uuid import uuid4, UUID
from datetime import datetime

from domain.entities.transaction import Transaction, TransactionType

def test_create_deposit_transaction():
    account_id = uuid4()
    transaction = Transaction.create_deposit(account_id, 100.0)
    assert transaction.account_id == account_id
    assert transaction.transaction_type == TransactionType.DEPOSIT
    assert transaction.amount == 100.0
    assert isinstance(transaction.transaction_id, UUID)
    assert isinstance(transaction.timestamp, datetime)

def test_create_withdrawal_transaction():
    account_id = uuid4()
    transaction = Transaction.create_withdrawal(account_id, 50.0)
    assert transaction.account_id == account_id
    assert transaction.transaction_type == TransactionType.WITHDRAW
    assert transaction.amount == 50.0
    assert isinstance(transaction.transaction_id, UUID)
    assert isinstance(transaction.timestamp, datetime)

def test_create_transfer_transaction():
    source_id = uuid4()
    dest_id = uuid4()
    transaction = Transaction.create_transfer(source_id, dest_id, 75.0)
    assert transaction.account_id == source_id
    assert transaction.transaction_type == TransactionType.TRANSFER
    assert transaction.amount == 75.0
    assert transaction.destination_account_id == dest_id
    assert isinstance(transaction.transaction_id, UUID)
    assert isinstance(transaction.timestamp, datetime)
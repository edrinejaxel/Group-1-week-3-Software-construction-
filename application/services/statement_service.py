from uuid import UUID
from datetime import datetime
from typing import List

from domain.entities.account import Account
from domain.entities.transaction import Transaction
from domain.exceptions.domain_exceptions import AccountNotFoundError
from infrastructure.repositories.account_repository import AccountRepository
from infrastructure.repositories.transaction_repository import TransactionRepository
from infrastructure.adapters.statement_adapter import StatementAdapter, Statement

class StatementService:
    def __init__(
        self,
        account_repository: AccountRepository,
        transaction_repository: TransactionRepository,
        statement_adapter: StatementAdapter
    ):
        self.account_repository = account_repository
        self.transaction_repository = transaction_repository
        self.statement_adapter = statement_adapter

    def generate_statement(self, account_id: UUID, start_date: datetime, end_date: datetime) -> Statement:
        account = self.account_repository.get_account_by_id(account_id)
        if not account:
            raise AccountNotFoundError(f"Account {account_id} not found")

        transactions = self.transaction_repository.get_transactions_for_account(account_id)
        
        # Convert timestamps to naive UTC if they're timezone-aware
        def normalize_timestamp(dt: datetime) -> datetime:
            if dt.tzinfo is not None:
                return dt.replace(tzinfo=None)
            return dt

        # Ensure all timestamps are naive
        start_date = normalize_timestamp(start_date)
        end_date = normalize_timestamp(end_date)
        
        filtered_transactions = [
            t for t in transactions
            if start_date <= normalize_timestamp(t.timestamp) <= end_date
        ]
        
        return self.statement_adapter.generate(
            account=account,
            transactions=filtered_transactions,
            start_date=start_date,
            end_date=end_date
        )
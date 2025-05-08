from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List
import csv
from io import StringIO

from domain.entities.account import Account
from domain.entities.transaction import Transaction

@dataclass
class Statement:
    account: Account
    transactions: List[Transaction]
    start_date: datetime
    end_date: datetime

class StatementAdapter(ABC):
    @abstractmethod
    def generate(
        self,
        account: Account,
        transactions: List[Transaction],
        start_date: datetime,
        end_date: datetime
    ) -> Statement:
        pass

class MockStatementAdapter(StatementAdapter):
    def generate(
        self,
        account: Account,
        transactions: List[Transaction],
        start_date: datetime,
        end_date: datetime
    ) -> Statement:
        return Statement(
            account=account,
            transactions=transactions,
            start_date=start_date,
            end_date=end_date
        )

class CSVStatementAdapter(StatementAdapter):
    def generate(
        self,
        account: Account,
        transactions: List[Transaction],
        start_date: datetime,
        end_date: datetime
    ) -> Statement:
        # Create a Statement object
        statement = Statement(
            account=account,
            transactions=transactions,
            start_date=start_date,
            end_date=end_date
        )
        # Generate CSV content as a string
        output = StringIO()
        writer = csv.writer(output)
        # Write header
        writer.writerow([
            "Account ID",
            "Account Type",
            "Balance",
            "Transaction ID",
            "Type",
            "Amount",
            "Timestamp",
            "Destination Account"
        ])
        # Write transaction rows
        for transaction in statement.transactions:
            writer.writerow([
                str(statement.account.account_id),
                statement.account.account_type.value,
                statement.account.balance,
                str(transaction.transaction_id),
                transaction.transaction_type.value,
                transaction.amount,
                transaction.timestamp.isoformat(),
                str(transaction.destination_account_id) if transaction.destination_account_id else ""
            ])
        # Store CSV content in the statement (for API to return)
        statement.csv_content = output.getvalue()
        output.close()
        return statement
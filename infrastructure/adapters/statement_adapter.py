from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import csv
from io import StringIO
from fpdf import FPDF
from domain.entities.account import Account
from domain.entities.transaction import Transaction, TransactionType 

@dataclass
class Statement:
    account: Account
    transactions: List[Transaction]
    start_date: datetime
    end_date: datetime
    csv_content: Optional[str] = None
    pdf_content: Optional[bytes] = None
    summary: Optional[dict] = None

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

    def _calculate_summary(self, transactions: List[Transaction]) -> dict:
        total_deposits = sum(t.amount for t in transactions if t.transaction_type == TransactionType.DEPOSIT)
        total_withdrawals = sum(t.amount for t in transactions if t.transaction_type == TransactionType.WITHDRAW)
        
        return {
            "total_transactions": len(transactions),
            "total_deposits": total_deposits,
            "total_withdrawals": total_withdrawals,
            "net_change": total_deposits - total_withdrawals
        }

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

class EnhancedCSVStatementAdapter(StatementAdapter):
    def generate(
        self,
        account: Account,
        transactions: List[Transaction],
        start_date: datetime,
        end_date: datetime
    ) -> Statement:
        output = StringIO()
        writer = csv.writer(output)
        
        # Write account summary
        writer.writerow(["Account Summary"])
        writer.writerow(["Account ID", str(account.account_id)])
        writer.writerow(["Account Type", account.account_type.value])
        writer.writerow(["Current Balance", f"${account.balance:.2f}"])
        writer.writerow(["Statement Period", f"{start_date.date()} to {end_date.date()}"])
        writer.writerow([])

        # Write transaction details
        writer.writerow([
            "Date",
            "Transaction ID",
            "Type",
            "Amount",
            "Balance After",
            "Description"
        ])

        running_balance = account.balance
        for transaction in reversed(transactions):
            if transaction.transaction_type == TransactionType.WITHDRAW:
                running_balance += transaction.amount
            elif transaction.transaction_type == TransactionType.DEPOSIT:
                running_balance -= transaction.amount

            writer.writerow([
                transaction.timestamp.strftime("%Y-%m-%d %H:%M"),
                str(transaction.transaction_id),
                transaction.transaction_type.value,
                f"${transaction.amount:.2f}",
                f"${running_balance:.2f}",
                self._get_transaction_description(transaction)
            ])

        # Calculate and write summary
        summary = self._calculate_summary(transactions)
        writer.writerow([])
        writer.writerow(["Transaction Summary"])
        writer.writerow(["Total Transactions", summary["total_transactions"]])
        writer.writerow(["Total Deposits", f"${summary['total_deposits']:.2f}"])
        writer.writerow(["Total Withdrawals", f"${summary['total_withdrawals']:.2f}"])
        writer.writerow(["Net Change", f"${summary['net_change']:.2f}"])

        return Statement(
            account=account,
            transactions=transactions,
            start_date=start_date,
            end_date=end_date,
            csv_content=output.getvalue(),
            summary=summary
        )

    def _get_transaction_description(self, transaction: Transaction) -> str:
        if transaction.transaction_type == TransactionType.TRANSFER:
            return f"Transfer to account {transaction.destination_account_id}"
        return f"{transaction.transaction_type.value.capitalize()} transaction"

class PDFStatementAdapter(StatementAdapter):
    def generate(
        self,
        account: Account,
        transactions: List[Transaction],
        start_date: datetime,
        end_date: datetime
    ) -> Statement:
        pdf = FPDF()
        pdf.add_page()
        
        # Header
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'Account Statement', 0, 1, 'C')
        
        # Account Information
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f'Account: {account.account_id}', 0, 1)
        pdf.cell(0, 10, f'Type: {account.account_type.value}', 0, 1)
        pdf.cell(0, 10, f'Period: {start_date.date()} to {end_date.date()}', 0, 1)
        pdf.cell(0, 10, f'Current Balance: ${account.balance:.2f}', 0, 1)
        
        # Transactions Table
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(30, 10, 'Date', 1)
        pdf.cell(30, 10, 'Type', 1)
        pdf.cell(30, 10, 'Amount', 1)
        pdf.cell(40, 10, 'Balance', 1)
        pdf.cell(0, 10, 'Description', 1, 1)
        
        # Transaction rows
        pdf.set_font('Arial', '', 10)
        running_balance = account.balance
        for transaction in reversed(transactions):
            if transaction.transaction_type == TransactionType.WITHDRAW:
                running_balance += transaction.amount
            elif transaction.transaction_type == TransactionType.DEPOSIT:
                running_balance -= transaction.amount
                
            pdf.cell(30, 10, transaction.timestamp.strftime("%Y-%m-%d"), 1)
            pdf.cell(30, 10, transaction.transaction_type.value, 1)
            pdf.cell(30, 10, f"${transaction.amount:.2f}", 1)
            pdf.cell(40, 10, f"${running_balance:.2f}", 1)
            pdf.cell(0, 10, self._get_transaction_description(transaction), 1, 1)

        # Summary
        summary = self._calculate_summary(transactions)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Transaction Summary', 0, 1, 'L')
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 10, f"Total Transactions: {summary['total_transactions']}", 0, 1)
        pdf.cell(0, 10, f"Total Deposits: ${summary['total_deposits']:.2f}", 0, 1)
        pdf.cell(0, 10, f"Total Withdrawals: ${summary['total_withdrawals']:.2f}", 0, 1)
        pdf.cell(0, 10, f"Net Change: ${summary['net_change']:.2f}", 0, 1)

        return Statement(
            account=account,
            transactions=transactions,
            start_date=start_date,
            end_date=end_date,
            pdf_content=pdf.output(dest='S').encode('latin1'),
            summary=summary
        )

    def _get_transaction_description(self, transaction: Transaction) -> str:
        if transaction.transaction_type == TransactionType.TRANSFER:
            return f"Transfer to {transaction.destination_account_id}"
        return f"{transaction.transaction_type.value.capitalize()}"
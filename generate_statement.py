from datetime import datetime, timedelta
from infrastructure.adapters.statement_adapter import EnhancedCSVStatementAdapter, PDFStatementAdapter
from infrastructure.repositories.account_repository import InMemoryAccountRepository
from infrastructure.repositories.transaction_repository import InMemoryTransactionRepository
from domain.entities.account import Account, AccountType
from domain.entities.transaction import Transaction, TransactionType
from uuid import uuid4

def generate_sample_statement():
    # Create repositories
    account_repo = InMemoryAccountRepository()
    transaction_repo = InMemoryTransactionRepository()

    # Create an account
    account = Account.create(AccountType.CHECKING, initial_deposit=1000.0)
    account_repo.create_account(account)

    # Create some sample transactions
    transactions = [
        Transaction(
            transaction_id=uuid4(),
            account_id=account.account_id,
            transaction_type=TransactionType.DEPOSIT,
            amount=500.0,
            timestamp=datetime.utcnow() - timedelta(days=5)
        ),
        Transaction(
            transaction_id=uuid4(),
            account_id=account.account_id,
            transaction_type=TransactionType.WITHDRAW,
            amount=200.0,
            timestamp=datetime.utcnow() - timedelta(days=2)
        )
    ]

    # Store transactions
    for tx in transactions:
        transaction_repo.save_transaction(tx)

    # Generate CSV statement
    csv_adapter = EnhancedCSVStatementAdapter()
    csv_statement = csv_adapter.generate(
        account=account,
        transactions=transactions,
        start_date=datetime.utcnow() - timedelta(days=30),
        end_date=datetime.utcnow()
    )

    # Generate PDF statement
    pdf_adapter = PDFStatementAdapter()
    pdf_statement = pdf_adapter.generate(
        account=account,
        transactions=transactions,
        start_date=datetime.utcnow() - timedelta(days=30),
        end_date=datetime.utcnow()
    )

    # Save statements to files
    with open(f'statement_{account.account_id}.csv', 'w') as f:
        f.write(csv_statement.csv_content)

    with open(f'statement_{account.account_id}.pdf', 'wb') as f:
        f.write(pdf_statement.pdf_content)

    print(f"Generated statements for account {account.account_id}")
    print(f"CSV Statement saved as: statement_{account.account_id}.csv")
    print(f"PDF Statement saved as: statement_{account.account_id}.pdf")

if __name__ == "__main__":
    generate_sample_statement()
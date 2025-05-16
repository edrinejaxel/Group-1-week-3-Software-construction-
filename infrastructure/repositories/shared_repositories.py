from infrastructure.repositories.account_repository import InMemoryAccountRepository
from infrastructure.repositories.transaction_repository import InMemoryTransactionRepository

# Create single instances to be shared across the application
account_repo = InMemoryAccountRepository()
transaction_repo = InMemoryTransactionRepository() 
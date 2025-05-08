from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel
from application.services.statement_service import StatementService
from infrastructure.repositories.account_repository import InMemoryAccountRepository
from infrastructure.repositories.transaction_repository import InMemoryTransactionRepository
from infrastructure.adapters.statement_adapter import CSVStatementAdapter
from domain.exceptions.domain_exceptions import AccountNotFoundError

router = APIRouter()

# Initialize repositories and services
account_repository = InMemoryAccountRepository()
transaction_repository = InMemoryTransactionRepository()
statement_adapter = CSVStatementAdapter()
statement_service = StatementService(account_repository, transaction_repository, statement_adapter)

class StatementRequest(BaseModel):
    start_date: datetime
    end_date: datetime

@router.get("/{account_id}", response_model=dict)
async def get_statement(account_id: UUID, request: StatementRequest = Depends()):
    try:
        statement = statement_service.generate_statement(account_id, request.start_date, request.end_date)
        return {
            "account_id": str(statement.account.account_id),
            "account_type": statement.account.account_type.value,
            "balance": statement.account.balance,
            "transactions": [
                {
                    "transaction_id": str(t.transaction_id),
                    "type": t.transaction_type.value,
                    "amount": t.amount,
                    "timestamp": t.timestamp.isoformat()
                } for t in statement.transactions
            ],
            "start_date": statement.start_date.isoformat(),
            "end_date": statement.end_date.isoformat(),
            "csv_content": getattr(statement, "csv_content", None)
        }
    except AccountNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
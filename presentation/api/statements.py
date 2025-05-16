from fastapi import APIRouter, HTTPException, Depends, Response, Query
from fastapi.responses import StreamingResponse
from uuid import UUID
from datetime import datetime
import io
import os
from typing import Optional
from tempfile import NamedTemporaryFile
from pydantic import BaseModel, validator
from application.services.statement_service import StatementService
from infrastructure.repositories.account_repository import InMemoryAccountRepository
from infrastructure.repositories.transaction_repository import InMemoryTransactionRepository
from infrastructure.adapters.statement_adapter import CSVStatementAdapter
from domain.exceptions.domain_exceptions import AccountNotFoundError
from infrastructure.repositories.shared_repositories import account_repo, transaction_repo

router = APIRouter()

statement_adapter = CSVStatementAdapter()
statement_service = StatementService(account_repo, transaction_repo, statement_adapter)

class StatementRequest(BaseModel):
    start_date: datetime
    end_date: datetime

    @validator('start_date', 'end_date')
    def convert_to_naive(cls, v):
        # If the datetime is timezone-aware, convert to naive UTC
        if v.tzinfo is not None:
            return v.replace(tzinfo=None)
        return v

    @validator('end_date')
    def end_date_must_be_after_start_date(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v

@router.get("/{account_id}")
async def get_statement(
    account_id: UUID,
    start_date: str = Query(..., description="Start date for the statement period (format: YYYY-MM-DDTHH:MM:SS)"),
    end_date: str = Query(..., description="End date for the statement period (format: YYYY-MM-DDTHH:MM:SS)"),
):
    try:
        # Convert string dates to datetime objects
        try:
            start_date_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end_date_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError("Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")

        # Validate dates
        if end_date_dt < start_date_dt:
            raise ValueError("end_date must be after start_date")
            
        # Convert to naive UTC
        start_date_dt = start_date_dt.replace(tzinfo=None)
        end_date_dt = end_date_dt.replace(tzinfo=None)

        # First check if account exists
        account = account_repo.get_account_by_id(account_id)
        if not account:
            raise AccountNotFoundError(f"Account {account_id} not found")

        # Generate statement
        statement = statement_service.generate_statement(account_id, start_date_dt, end_date_dt)
        
        # Return JSON response
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
            "csv_content": statement.csv_content
        }
    except AccountNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Log the error for debugging
        print(f"Error generating statement: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred while generating the statement: {str(e)}")

@router.get("/{account_id}/csv")
async def get_statement_csv(
    account_id: UUID,
    start_date: str = Query(..., description="Start date for the statement period (format: YYYY-MM-DDTHH:MM:SS)"),
    end_date: str = Query(..., description="End date for the statement period (format: YYYY-MM-DDTHH:MM:SS)"),
):
    try:
        # Convert string dates to datetime objects
        try:
            start_date_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end_date_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError("Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")

        # Validate dates
        if end_date_dt < start_date_dt:
            raise ValueError("end_date must be after start_date")
            
        # Convert to naive UTC
        start_date_dt = start_date_dt.replace(tzinfo=None)
        end_date_dt = end_date_dt.replace(tzinfo=None)

        # First check if account exists
        account = account_repo.get_account_by_id(account_id)
        if not account:
            raise AccountNotFoundError(f"Account {account_id} not found")

        # Generate statement
        statement = statement_service.generate_statement(account_id, start_date_dt, end_date_dt)
        
        # Return CSV file
        filename = f"statement_{account_id}_{start_date.split('T')[0]}_{end_date.split('T')[0]}.csv"
        return StreamingResponse(
            io.StringIO(statement.csv_content),
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except AccountNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Log the error for debugging
        print(f"Error generating statement: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred while generating the statement: {str(e)}")
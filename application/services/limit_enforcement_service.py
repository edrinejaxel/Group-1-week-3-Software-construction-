from uuid import UUID
from datetime import datetime, timedelta

from domain.entities.account import Account
from domain.exceptions.domain_exceptions import AccountNotFoundError
from infrastructure.repositories.account_repository import AccountRepository

class LimitEnforcementService:
    def __init__(self, account_repository: AccountRepository):
        self.account_repository = account_repository

    def set_limits(self, account_id: UUID, daily_limit: float, monthly_limit: float) -> None:
        account = self.account_repository.get_account_by_id(account_id)
        if not account:
            raise AccountNotFoundError(f"Account {account_id} not found")
        from domain.services.limit_constraint import LimitConstraint
        account.limit_constraint = LimitConstraint(
            daily_limit=daily_limit,
            monthly_limit=monthly_limit
        )
        self.account_repository.update_account(account)

    def reset_limits(self, account_id: UUID) -> None:
        account = self.account_repository.get_account_by_id(account_id)
        if not account:
            raise AccountNotFoundError(f"Account {account_id} not found")
        account.reset_limits(datetime.utcnow() + timedelta(days=1))
        self.account_repository.update_account(account)
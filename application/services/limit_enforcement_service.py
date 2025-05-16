from uuid import UUID
from datetime import datetime
from domain.services.limit_constraint import LimitConstraint
from domain.exceptions.domain_exceptions import AccountNotFoundError

class LimitEnforcementService:
    def __init__(self, account_repository):
        self.account_repository = account_repository

    def set_limits(self, account_id: UUID, daily_limit: float, monthly_limit: float) -> None:
        account = self.account_repository.get_account_by_id(account_id)
        if not account:
            raise AccountNotFoundError(f"Account {account_id} not found")

        # Create new limit constraint
        account.limit_constraint = LimitConstraint(
            daily_limit=daily_limit,
            monthly_limit=monthly_limit
        )
        
        # Update account in repository
        self.account_repository.update_account(account)

    def reset_limits(self, account_id: UUID) -> None:
        account = self.account_repository.get_account_by_id(account_id)
        if not account:
            raise AccountNotFoundError(f"Account {account_id} not found")

        # Reset limits directly
        account.daily_spent = 0.0
        account.monthly_spent = 0.0
        account.transaction_count = 0

        # Call reset_limits with current date
        account.reset_limits(datetime.utcnow())
        self.account_repository.update_account(account)
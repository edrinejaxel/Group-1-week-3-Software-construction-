from dataclasses import dataclass
import domain
from domain.exceptions.domain_exceptions import TransactionLimitExceededError

@dataclass
class LimitConstraint:
    daily_limit: float
    monthly_limit: float

    def check_deposit(self, account: "domain.entities.account.Account", amount: float) -> None:
        pass

    def check_withdrawal(self, account: "domain.entities.account.Account", amount: float) -> None:
        new_daily_spent = account.daily_spent + amount
        new_monthly_spent = account.monthly_spent + amount
        if new_daily_spent > self.daily_limit:
            raise TransactionLimitExceededError("Daily withdrawal limit exceeded")
        if new_monthly_spent > self.monthly_limit:
            raise TransactionLimitExceededError("Monthly withdrawal limit exceeded")
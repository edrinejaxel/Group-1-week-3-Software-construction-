
class Account:
    def __init__(self, account_id, balance, interest_strategy):
        self.account_id = account_id
        self.balance = balance
        self.interest_strategy = interest_strategy

    def calculate_interest(self):
        return self.interest_strategy.calculate(self.balance)

class AccountWithLimits(Account):
    def __init__(self, account_id, balance, interest_strategy, daily_limit, monthly_limit):
        super().__init__(account_id, balance, interest_strategy)
        self.daily_limit = daily_limit
        self.monthly_limit = monthly_limit
        self.daily_spent = 0
        self.monthly_spent = 0

    def deposit(self, amount):
        if self.daily_spent + amount > self.daily_limit:
            raise ValueError("Daily limit exceeded.")
        self.balance += amount
        self.daily_spent += amount
        self.monthly_spent += amount

    def withdraw(self, amount):
        if self.daily_spent + amount > self.daily_limit:
            raise ValueError("Daily limit exceeded.")
        self.balance -= amount
        self.daily_spent += amount
        self.monthly_spent += amount

    def reset_limits(self):
        self.daily_spent = 0
        self.monthly_spent = 0


class MonthlyStatement:
    def __init__(self, account):
        self.account = account
        self.interest_accrued = account.calculate_interest()
        self.transaction_totals = account.daily_spent  # Simplified for this example
        self.final_balance = account.balance

    def generate_statement(self):
        return {
            "Account ID": self.account.account_id,
            "Interest Accrued": self.interest_accrued,
            "Transaction Totals": self.transaction_totals,
            "Final Balance": self.final_balance,
        }

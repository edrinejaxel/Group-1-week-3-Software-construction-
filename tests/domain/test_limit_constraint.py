import pytest

from domain.services.interest_strategy import CheckingInterestStrategy, SavingsInterestStrategy

def test_checking_interest_strategy():
    strategy = CheckingInterestStrategy()
    interest = strategy.calculate_interest(1000.0)
    assert interest == 10.0  # 1% of 1000

def test_savings_interest_strategy():
    strategy = SavingsInterestStrategy()
    interest = strategy.calculate_interest(1000.0)
    assert interest == 30.0  # 3% of 1000

from abc import ABC, abstractmethod

class InterestStrategy(ABC):
    @abstractmethod
    def calculate(self, balance):
        pass

class SimpleInterestStrategy(InterestStrategy):
    def calculate(self, balance):
        rate = 0.05  # Example interest rate
        return balance * rate

class CompoundInterestStrategy(InterestStrategy):
    def calculate(self, balance):
        rate = 0.05  # Example interest rate
        return balance * (1 + rate) ** 1 - balance  # For one period

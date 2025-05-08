from abc import ABC, abstractmethod

class InterestStrategy(ABC):
    @abstractmethod
    def calculate_interest(self, balance: float) -> float:
        pass

class CheckingInterestStrategy(InterestStrategy):
    def calculate_interest(self, balance: float) -> float:
        return balance * 0.01  # 1% annual interest, simplified

class SavingsInterestStrategy(InterestStrategy):
    def calculate_interest(self, balance: float) -> float:
        return balance * 0.03  # 3% annual interest, simplified
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict

@dataclass
class InterestConfig:
    base_rate: float
    minimum_balance_rate: float
    minimum_balance_threshold: float
    maximum_rate: float

class InterestStrategy(ABC):
    @abstractmethod
    def calculate_interest(self, balance: float) -> float:
        pass

class ConfigurableInterestStrategy(InterestStrategy):
    def __init__(self, config: InterestConfig):
        self.config = config

    def calculate_interest(self, balance: float) -> float:
        if balance <= 0:
            return 0.0
            
        # Start with base rate
        rate = self.config.base_rate
        
        # Add bonus rate for maintaining minimum balance
        if balance >= self.config.minimum_balance_threshold:
            rate += self.config.minimum_balance_rate
            
        # Cap at maximum rate
        rate = min(rate, self.config.maximum_rate)
        
        return balance * rate

class ConfigurableCheckingInterestStrategy(ConfigurableInterestStrategy):
    DEFAULT_CONFIG = InterestConfig(
        base_rate=0.01,  # 1% base
        minimum_balance_rate=0.005,  # 0.5% bonus
        minimum_balance_threshold=1000.0,
        maximum_rate=0.02  # 2% maximum
    )

    def __init__(self, config: InterestConfig = None):
        super().__init__(config or self.DEFAULT_CONFIG)

class ConfigurableSavingsInterestStrategy(ConfigurableInterestStrategy):
    DEFAULT_CONFIG = InterestConfig(
        base_rate=0.02,  # 2% base
        minimum_balance_rate=0.01,  # 1% bonus
        minimum_balance_threshold=5000.0,
        maximum_rate=0.04  # 4% maximum
    )

    def __init__(self, config: InterestConfig = None):
        super().__init__(config or self.DEFAULT_CONFIG)
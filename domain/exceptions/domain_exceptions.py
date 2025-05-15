class DomainError(Exception):
    pass

class InsufficientFundsError(DomainError):
    pass

class InvalidAmountError(DomainError):
    pass

class InvalidAccountStatusError(DomainError):
    pass

class AccountNotFoundError(DomainError):
    pass

class TransactionLimitExceededError(DomainError):
    pass

class AccountLockedError(Exception):
    pass

class TransactionLimitError(Exception):
    pass

class MinimumBalanceError(Exception):
    pass
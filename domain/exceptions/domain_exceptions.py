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
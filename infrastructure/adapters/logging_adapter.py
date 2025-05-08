import logging
from functools import wraps
from typing import Callable, Any

class LoggingAdapter:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def log_method(self, method: Callable) -> Callable:
        @wraps(method)
        def wrapper(*args, **kwargs) -> Any:
            self.logger.info(f"Calling {method.__name__} with args: {args}, kwargs: {kwargs}")
            result = method(*args, **kwargs)
            self.logger.info(f"{method.__name__} returned: {result}")
            return result
        return wrapper
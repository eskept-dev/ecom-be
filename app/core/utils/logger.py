import logging
import time
from functools import wraps
from typing import Any, Callable

# Get logger for the app
logger = logging.getLogger('app')

def log_execution_time(func: Callable) -> Callable:
    """
    Decorator to log the execution time of a function
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.debug(f"{func.__name__} executed in {execution_time:.2f} seconds")
        return result
    return wrapper

def log_exception(func: Callable) -> Callable:
    """
    Decorator to log exceptions in a function
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.exception(f"Exception in {func.__name__}: {str(e)}")
            raise
    return wrapper

class LoggerMixin:
    """
    Mixin to add logging capabilities to a class
    """
    @property
    def logger(self):
        return logging.getLogger(f"app.{self.__class__.__name__}") 
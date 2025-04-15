"""Utility module for retrying operations with exponential backoff.

This module provides functions for retrying operations that might fail temporarily
but could succeed after retrying with appropriate delays between attempts.
"""

import datetime
import time
from typing import TypeVar, Callable, Optional

import requests.exceptions

import seventeenlands.logging_utils

T = TypeVar("T")  # Generic type for function return values

logger = seventeenlands.logging_utils.get_logger("retry_utils")

# Default retry parameters
_INITIAL_RETRY_DELAY = datetime.timedelta(seconds=1)
_MAX_RETRY_DELAY = datetime.timedelta(minutes=10)
_MAX_TOTAL_RETRY_DURATION = datetime.timedelta(hours=24)


class RetryLimitExceededError(Exception):
    """Exception raised when retry attempts exceed the maximum allowed duration."""

    pass


def retry_until_successful(
    callback: Callable[[], T],
    response_validator: Callable[[T], bool],
    error_validator: Callable[[Exception], bool],
    initial_retry_delay: datetime.timedelta,
    max_retry_delay: Optional[datetime.timedelta],
    max_total_retry_duration: Optional[datetime.timedelta],
) -> T:
    """Retry a function call until it succeeds or exceeds retry limits.

    Args:
        callback: Function to call that returns a result of type T.
        response_validator: Function that validates if the response is acceptable.
        error_validator: Function that determines if an exception should trigger a retry.
        initial_retry_delay: Initial delay between retry attempts.
        max_retry_delay: Maximum delay between retry attempts (caps exponential growth).
        max_total_retry_duration: Maximum total time to spend on retries.

    Returns:
        The successful result from the callback function.

    Raises:
        RetryLimitExceededError: When max_total_retry_duration is exceeded.
        Exception: Re-raises any exception from callback that error_validator rejects.
    """
    last_call_at: Optional[datetime.datetime] = None
    if max_total_retry_duration:
        # Calculate absolute deadline time
        last_call_at = datetime.datetime.utcnow() + max_total_retry_duration

    next_retry_delay = initial_retry_delay
    while True:
        # Check if we've exceeded the total retry duration
        is_last_call = (
            last_call_at is not None and last_call_at < datetime.datetime.utcnow()
        )
        try:
            result = callback()
            if response_validator(result):
                # Return the result
                return result
            elif is_last_call:
                # Exceeded max retry duration with invalid result
                raise RetryLimitExceededError()
        except Exception as e:
            if is_last_call or not error_validator(e):
                # Either exceeded retry time or encountered non-retryable error
                raise e

        # Sleep before next retry attempt
        time.sleep(next_retry_delay.total_seconds())
        # Implement exponential backoff (double the delay each time)
        next_retry_delay *= 2
        if max_retry_delay and max_retry_delay < next_retry_delay:
            # Cap the delay at max_retry_delay
            next_retry_delay = max_retry_delay


def retry_api_call(
    callback: Callable[[], T],
    response_validator: Callable[[T], bool],
) -> T:
    """Retry an API call with predefined retry parameters.

    This is a specialized version of retry_until_successful configured for API calls,
    automatically handling common API-related errors like connection issues.

    Args:
        callback: API call function to retry.
        response_validator: Function to validate if the API response is acceptable.

    Returns:
        The successful result from the API call.

    Raises:
        Exception: Any exception from the API call that isn't retryable.
    """

    def _should_retry_error(error: Exception) -> bool:
        """Determine if an error should trigger a retry for API calls.

        Args:
            error: The exception that occurred during the API call.

        Returns:
            True if the error is retryable, False otherwise.
        """
        logger.exception(f"Error: {error}")
        error_class = type(error)
        if issubclass(error_class, requests.exceptions.ConnectionError):
            # Retry connection errors
            return True
        return False

    return retry_until_successful(
        callback=callback,
        response_validator=response_validator,
        error_validator=_should_retry_error,
        initial_retry_delay=_INITIAL_RETRY_DELAY,
        max_retry_delay=_MAX_RETRY_DELAY,
        max_total_retry_duration=_MAX_TOTAL_RETRY_DURATION,
    )

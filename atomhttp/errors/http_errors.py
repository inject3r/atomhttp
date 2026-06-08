"""
HTTP Error Module
-----------------
Custom exception classes for AtomHTTP client error handling.

This module provides a hierarchy of exception classes for different types
of HTTP request failures, similar to axios error handling. Each error type
includes relevant context such as request configuration, response data,
and error codes for programmatic error identification.
"""

from typing import Optional, Any


class AtomHTTPError(Exception):
    """
    Base exception class for all AtomHTTP errors.
    
    This is the parent class for all AtomHTTP-specific exceptions. It provides
    common attributes that are useful for debugging and error handling.
    
    Attributes:
        message (str): Human-readable error description
        config (Optional[Any]): Request configuration that caused the error
        response (Optional[Any]): Response object if error occurred after receiving response
        request (Optional[Any]): Original request configuration (alias for config)
        code (Optional[str]): Standardized error code for programmatic handling
    """
    
    def __init__(
        self,
        message: str,
        config: Optional[Any] = None,
        response: Optional[Any] = None,
        request: Optional[Any] = None
    ):
        """
        Initialize a AtomHTTP error with optional context.
        
        Args:
            message (str): Human-readable error description
            config (Optional[Any]): Request configuration used for the request
            response (Optional[Any]): Response object (if available)
            request (Optional[Any]): Original request (usually same as config)
        """
        super().__init__(message)
        self.message = message
        self.config = config
        self.response = response
        self.request = request
        self.code: Optional[str] = None


class AtomHTTPRequestError(AtomHTTPError):
    """
    Exception raised for bad requests or client errors (4xx status codes).
    
    This error occurs when the request is malformed, validation fails,
    or the server responds with a client error status code (400-499).
    
    Error Code: 'ERR_BAD_REQUEST'
    
    Attributes:
        code (str): Standardized error code always set to 'ERR_BAD_REQUEST'
    """
    
    def __init__(
        self,
        message: str,
        request: Optional[Any] = None,
        config: Optional[Any] = None,
        response: Optional[Any] = None
    ):
        """
        Initialize a request error.
        
        Args:
            message (str): Error description
            request (Optional[Any]): Original request that failed
            config (Optional[Any]): Request configuration (alias for request)
            response (Optional[Any]): Response from server (if available)
        """
        super().__init__(message, config=config, response=response, request=request)
        self.code = 'ERR_BAD_REQUEST'


class AtomHTTPNetworkError(AtomHTTPError):
    """
    Exception raised for network-related failures.
    
    This error occurs when the request cannot reach the server due to
    network issues such as DNS resolution failure, connection refused,
    SSL errors, or general connectivity problems.
    
    Error Code: 'ERR_NETWORK'
    
    Attributes:
        code (str): Standardized error code always set to 'ERR_NETWORK'
    """
    
    def __init__(self, message: str, config: Optional[Any] = None):
        """
        Initialize a network error.
        
        Args:
            message (str): Error description (connection error, DNS error, etc.)
            config (Optional[Any]): Request configuration used for the request
        """
        super().__init__(message, config=config)
        self.code = 'ERR_NETWORK'


class AtomHTTPTimeoutError(AtomHTTPError):
    """
    Exception raised when a request exceeds the configured timeout.
    
    This error occurs when the request takes longer than the specified
    timeout value. The request may have been partially sent or the
    response may have been partially received before timeout occurred.
    
    Error Code: 'ECONNABORTED'
    
    Attributes:
        code (str): Standardized error code always set to 'ECONNABORTED'
    """
    
    def __init__(
        self,
        message: str,
        config: Optional[Any] = None,
        request: Optional[Any] = None
    ):
        """
        Initialize a timeout error.
        
        Args:
            message (str): Error description with timeout duration
            config (Optional[Any]): Request configuration used for the request
            request (Optional[Any]): Original request (alias for config)
        """
        super().__init__(message, config=config, request=request)
        self.code = 'ECONNABORTED'
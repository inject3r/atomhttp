"""
Response Module
---------------
HTTP response object for AtomHTTP client.

This module provides the Response class that wraps HTTP responses with
a consistent interface similar to axios responses. It includes response
data, status code, headers, and references to the original request
configuration.
"""

from typing import Any, Dict, Optional
from dataclasses import dataclass


@dataclass
class Response:
    """
    HTTP response object similar to axios response interface.
    
    This class encapsulates all components of an HTTP response including
    the parsed body, status information, headers, and the original request
    configuration. It provides a clean, consistent interface for accessing
    response data.
    
    The Response object is immutable by design (frozen dataclass semantics
    are not enforced but should be treated as read-only after creation).
    
    Attributes:
        data (Any): Parsed response body. Type depends on responseType:
                   - 'json': dict or list
                   - 'text': str
                   - 'blob'/'arraybuffer': bytes
                   - 'stream': aiohttp.StreamReader
        status (int): HTTP status code (e.g., 200, 404, 500)
        status_text (str): HTTP status message (e.g., "OK", "Not Found")
        headers (Dict[str, str]): Response headers as a case-insensitive dict
        config (Any): Original RequestConfig object used for the request
        request (Any): Reference to the original request configuration
                      (usually same as config, kept for axios compatibility)
    
    Properties:
        ok (bool): True if status code is in the 200-299 range
    
    Example:
        >>> response = Response(
        ...     data={'id': 1, 'name': 'John'},
        ...     status=200,
        ...     status_text='OK',
        ...     headers={'Content-Type': 'application/json'},
        ...     config=original_config,
        ...     request=original_config
        ... )
        >>> print(response.ok)
        True
        >>> print(response.status)
        200
    """
    
    data: Any
    status: int
    status_text: str
    headers: Dict[str, str]
    config: Any
    request: Any
    
    def __repr__(self) -> str:
        """
        Return a string representation of the response.
        
        Returns:
            str: Formatted response string with status code and message
        
        Example:
            >>> response = Response(data={}, status=200, status_text='OK', ...)
            >>> print(repr(response))
            '<Response [200] OK>'
        """
        return f"<Response [{self.status}] {self.status_text}>"
    
    @property
    def ok(self) -> bool:
        """
        Check if the response status indicates success.
        
        A response is considered "ok" when the HTTP status code falls within
        the 200-299 range (successful responses).
        
        Returns:
            bool: True if status code is between 200 and 299 inclusive,
                  False otherwise
        
        Example:
            >>> response = Response(data={}, status=200, status_text='OK', ...)
            >>> response.ok
            True
            >>> response = Response(data={}, status=404, status_text='Not Found', ...)
            >>> response.ok
            False
        """
        return 200 <= self.status < 300
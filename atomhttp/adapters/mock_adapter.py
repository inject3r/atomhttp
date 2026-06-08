"""
Mock Adapter Module
-------------------
This module provides a mock HTTP adapter for testing purposes.

The MockAdapter allows developers to simulate HTTP responses without making
actual network requests. This is useful for unit testing, integration testing,
and development scenarios where external APIs are unavailable or undesirable
to call directly.
"""

from typing import Dict, Any, Optional
from ..core.config import RequestConfig
from ..core.response import Response


class MockAdapter:
    """
    Mock adapter for testing HTTP requests without actual network calls.
    
    This adapter stores predefined responses for specific request patterns
    and returns them when matching requests are made. It enables isolated
    testing of code that depends on HTTP responses without external dependencies.
    
    Features:
        - Register mock responses for specific HTTP methods and URLs
        - Customizable response data, status codes, and status texts
        - Automatic 404 response for unregistered endpoints
        - No actual network connections are established
    
    Attributes:
        _responses (Dict[str, Dict]): Internal storage mapping request keys
                                     to their configured mock responses.
    
    Example:
        >>> mock = MockAdapter()
        >>> mock.on('GET', 'https://api.test/users', {'users': []}, 200)
        >>> response = await mock.send(config)
    """
    
    def __init__(self):
        """
        Initialize an empty mock adapter with no predefined responses.
        
        Use the on() method to register mock responses before sending requests.
        """
        self._responses: Dict[str, Dict] = {}
    
    def on(self, method: str, url: str, response_data: Any, status: int = 200):
        """
        Register a mock response for a specific HTTP method and URL.
        
        When a request with the matching method and URL is sent through this
        adapter, the registered response will be returned instead of making
        an actual network request.
        
        Args:
            method (str): HTTP method (GET, POST, PUT, DELETE, etc.)
            url (str): Full URL or path that this mock should respond to
            response_data (Any): Data to be returned as the response body.
                                Can be dict, list, string, or any JSON-serializable type.
            status (int): HTTP status code to return. Defaults to 200.
        
        Note:
            If multiple responses are registered for the same method and URL,
            the last registration will overwrite previous ones.
        
        Example:
            >>> mock = MockAdapter()
            >>> mock.on('GET', 'https://api.test/users', {'users': []}, 200)
            >>> mock.on('POST', 'https://api.test/users', {'id': 1}, 201)
            >>> mock.on('GET', 'https://api.test/users/1', {'name': 'John'}, 200)
        """
        # Create a unique key combining method and URL for lookup
        key = f"{method}:{url}"
        
        # Store the mock response configuration
        self._responses[key] = {
            'data': response_data,
            'status': status,
            'status_text': 'OK' if status == 200 else 'Error'
        }
    
    async def send(self, config: RequestConfig) -> Response:
        """
        Send a mock request and return a predefined response.
        
        This method looks up the request method and URL in the registered
        responses. If a match is found, the corresponding mock response is
        returned. Otherwise, a 404 Not Found response is returned.
        
        Args:
            config (RequestConfig): Request configuration containing method and URL.
                                   Other config fields (headers, data, etc.) are
                                   ignored in mock mode.
        
        Returns:
            Response: A AtomHTTP Response object containing either the registered
                     mock data or a 404 error response.
        
        Note:
            No actual HTTP request is made. The response is constructed entirely
            from in-memory mock data, making this adapter suitable for tests
            that require deterministic, repeatable responses.
        """
        # Build lookup key from request configuration
        key = f"{config.method}:{config.url}"
        
        # Check if a mock response is registered for this request
        if key in self._responses:
            mock = self._responses[key]
            # Return the registered mock response
            return Response(
                data=mock['data'],
                status=mock['status'],
                status_text=mock['status_text'],
                headers={},
                config=config,
                request=config
            )
        else:
            # Return default 404 response for unregistered endpoints
            return Response(
                data={'error': 'No mock found'},
                status=404,
                status_text='Not Found',
                headers={},
                config=config,
                request=config
            )
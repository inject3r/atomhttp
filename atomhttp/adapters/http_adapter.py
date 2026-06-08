"""
HTTP Adapter Module
-------------------
This module provides the base HTTP adapter for making asynchronous HTTP requests
using aiohttp. It handles request execution, timeout management, proxy support,
and response processing.

The HTTPAdapter is the default transport layer for the AtomHTTP client,
responsible for converting RequestConfig objects into actual HTTP requests
and wrapping responses into AtomHTTP Response objects.
"""

import aiohttp
from typing import Optional
from ..core.config import RequestConfig
from ..core.response import Response


class HTTPAdapter:
    """
    HTTP adapter for making asynchronous HTTP requests using aiohttp.
    
    This adapter serves as the transport layer for the AtomHTTP client,
    handling the low-level details of HTTP communication including connection
    management, timeout handling, proxy configuration, and response parsing.
    
    Attributes:
        proxy (Optional[str]): Proxy server URL to use for requests.
                              Format: 'http://proxy.example.com:8080'
    """
    
    def __init__(self, proxy: Optional[str] = None):
        """
        Initialize the HTTP adapter with optional proxy configuration.
        
        Args:
            proxy (Optional[str]): Proxy server URL. If provided, all requests
                                  will be routed through this proxy.
        """
        self.proxy = proxy
    
    async def send(self, config: RequestConfig) -> Response:
        """
        Execute an HTTP request based on the provided configuration.
        
        This method performs the actual HTTP request using aiohttp,
        handling all aspects of the request lifecycle including connection
        establishment, timeout management, request headers and body,
        redirect following, and response parsing.
        
        Args:
            config (RequestConfig): Request configuration object containing all
                                   request parameters such as URL, method,
                                   headers, data, timeout, etc.
        
        Returns:
            Response: A AtomHTTP Response object containing the parsed response
                     data, status code, headers, and original configuration.
        
        Raises:
            aiohttp.ClientError: If a network-related error occurs
            asyncio.TimeoutError: If the request exceeds the configured timeout
            json.JSONDecodeError: If response_type='json' and response is invalid JSON
        """
        # Configure timeout with total request duration limit
        timeout = aiohttp.ClientTimeout(total=config.timeout)
        
        # Create TCP connector if proxy is configured
        connector = None
        if self.proxy:
            connector = aiohttp.TCPConnector()
        
        # Create a new client session for this request
        # Using async context manager ensures proper cleanup
        async with aiohttp.ClientSession(connector=connector) as session:
            # Execute the HTTP request with all configured parameters
            async with session.request(
                method=config.method,
                url=config.url,
                headers=config.headers,
                params=config.params,
                data=config.data,
                timeout=timeout,
                max_redirects=config.maxRedirects
            ) as response:
                # Parse response body based on expected response type
                # JSON responses are automatically deserialized to dict/list
                # Non-JSON responses are returned as plain text
                if config.responseType == 'json':
                    data = await response.json()
                else:
                    data = await response.text()
                
                # Wrap the aiohttp response in AtomHTTP's Response object
                return Response(
                    data=data,
                    status=response.status,
                    status_text=response.reason,
                    headers=dict(response.headers),
                    config=config,
                    request=config
                )
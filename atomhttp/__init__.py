"""
AtomHTTP - Professional HTTP Client for Python
===============================================

A comprehensive, asynchronous HTTP client for Python with features including:
    - Full HTTP method support (GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS)
    - Request and response interceptors
    - Upload and download progress tracking
    - FormData (multipart/form-data) with file uploads
    - Blob, ArrayBuffer, and stream response types
    - Concurrent request helpers (all, spread)
    - Base URL configuration
    - Automatic JSON serialization/deserialization
    - Comprehensive error handling with typed exceptions
    - Type hints for better IDE support
    - Mock adapter for testing
    - Keep-alive connection pooling
    - Proxy support
    - Unix socket path support
    - Configurable timeouts and redirect limits

This module exports the main AtomHTTP client class along with all necessary
types, exceptions, and utilities for making HTTP requests.

Example:
    >>> import asyncio
    >>> from atomhttp import AtomHTTP
    >>> 
    >>> async def main():
    ...     client = AtomHTTP({'baseURL': 'https://api.example.com'})
    ...     response = await client.get('/users')
    ...     print(response.status, response.data)
    ...     await client.close()
    >>> 
    >>> asyncio.run(main())
"""

from .client import AtomHTTP
from .errors.http_errors import (
    AtomHTTPError,
    AtomHTTPRequestError,
    AtomHTTPNetworkError,
    AtomHTTPTimeoutError
)
from .core.response import Response
from .core.config import RequestConfig
from .core.form_data import FormData
from .core.adapters import HTTPAdapter, MockAdapter
from .interceptors.manager import InterceptorManager
from .version import __version__

__all__ = [
    # Main client
    "AtomHTTP",
    
    # Exception classes
    "AtomHTTPError",
    "AtomHTTPRequestError",
    "AtomHTTPNetworkError",
    "AtomHTTPTimeoutError",
    
    # Core types
    "Response",
    "RequestConfig",
    
    # Interceptor management
    "InterceptorManager",
    
    # Data types
    "FormData",
    
    # Adapters
    "HTTPAdapter",
    "MockAdapter",
]
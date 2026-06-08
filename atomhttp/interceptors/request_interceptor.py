"""
Request Interceptor Type Definition
-----------------------------------
Type hint for request interceptor functions in AtomHTTP.

This module defines the RequestInterceptor type alias for use in type annotations
throughout the AtomHTTP codebase. Request interceptors are functions that
modify or inspect request configurations before they are sent.
"""

from typing import Callable, Awaitable
from ..core.config import RequestConfig

# Type alias for request interceptor functions
# Request interceptors receive a RequestConfig object and return a
# (potentially modified) RequestConfig object. They can be either
# synchronous or asynchronous.
RequestInterceptor = Callable[[RequestConfig], Awaitable[RequestConfig]]
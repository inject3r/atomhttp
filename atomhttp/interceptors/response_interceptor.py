"""
Response Interceptor Type Definition
------------------------------------
Type hint for response interceptor functions in AtomHTTP.

This module defines the ResponseInterceptor type alias for use in type annotations
throughout the AtomHTTP codebase. Response interceptors are functions that
modify or inspect response objects before they are returned to the caller.
"""

from typing import Callable, Awaitable
from ..core.response import Response

# Type alias for response interceptor functions
# Response interceptors receive a Response object and return a
# (potentially modified) Response object. They can be either
# synchronous or asynchronous.
ResponseInterceptor = Callable[[Response], Awaitable[Response]]
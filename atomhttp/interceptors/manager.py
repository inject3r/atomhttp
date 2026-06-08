"""
Interceptor Manager Module
--------------------------
Manages request and response interceptors for the AtomHTTP client.

This module provides the InterceptorManager class which handles registration,
execution order, and removal of interceptors. Interceptors allow modifying
requests before they are sent and responses before they are returned to
the caller, similar to middleware in other HTTP clients.
"""

from typing import List, Callable, Any


class InterceptorManager:
    """
    Manages request and response interceptors for the HTTP client.
    
    Interceptors are functions that can modify requests before they are
    sent or modify responses before they are returned to the caller.
    This enables functionality such as:
        - Adding authentication headers to all requests
        - Logging requests and responses
        - Retrying failed requests
        - Transforming request/response data
        - Handling errors globally
    
    The interceptor execution order follows the registration order:
        - Request interceptors execute in the order they were added
        - Response interceptors execute in the order they were added
    
    Interceptors can be either synchronous or asynchronous functions.
    Asynchronous interceptors must be declared with `async def`.
    
    Attributes:
        request_interceptors (List[Callable]): List of request interceptor functions
        response_interceptors (List[Callable]): List of response interceptor functions
    """
    
    def __init__(self):
        """
        Initialize an empty interceptor manager.
        
        Both request and response interceptor lists start empty.
        Use the use() method to add interceptors.
        """
        self.request_interceptors: List[Callable] = []
        self.response_interceptors: List[Callable] = []
    
    def use(self, interceptor: Callable, is_response: bool = False) -> int:
        """
        Add an interceptor to the manager.
        
        The interceptor will be added to the end of the list and will
        be executed after all previously added interceptors.
        
        Args:
            interceptor (Callable): The interceptor function.
                                  Can be sync: `fn(config)` or `fn(response)`
                                  or async: `async fn(config)` or `async fn(response)`
            is_response (bool): If True, adds to response interceptors list.
                               If False (default), adds to request interceptors list.
        
        Returns:
            int: The index of the added interceptor. This index can be used
                with the eject() method to remove the interceptor later.
        
        Example:
            >>> manager = InterceptorManager()
            >>> 
            >>> # Request interceptor (adds auth header)
            >>> async def add_auth(config):
            ...     config.headers['Authorization'] = 'Bearer token'
            ...     return config
            >>> 
            >>> index = manager.use(add_auth)  # Request interceptor
            >>> 
            >>> # Response interceptor (logs response)
            >>> async def log_response(response):
            ...     print(f"Status: {response.status}")
            ...     return response
            >>> 
            >>> resp_index = manager.use(log_response, is_response=True)
        """
        if is_response:
            self.response_interceptors.append(interceptor)
            return len(self.response_interceptors) - 1
        else:
            self.request_interceptors.append(interceptor)
            return len(self.request_interceptors) - 1
    
    def eject(self, index: int, is_response: bool = False) -> None:
        """
        Remove an interceptor by its index.
        
        This method removes the interceptor at the specified index from
        either the request or response interceptor list. The index must
        be the one returned by the use() method when the interceptor
        was added.
        
        Args:
            index (int): Index of the interceptor to remove
            is_response (bool): If True, removes from response interceptors list.
                               If False (default), removes from request interceptors list.
        
        Example:
            >>> manager = InterceptorManager()
            >>> index = manager.use(some_interceptor)
            >>> # Later...
            >>> manager.eject(index)  # Remove the interceptor
        
        Note:
            If the index is out of range, the method does nothing (no error raised).
        """
        if is_response:
            if 0 <= index < len(self.response_interceptors):
                self.response_interceptors.pop(index)
        else:
            if 0 <= index < len(self.request_interceptors):
                self.request_interceptors.pop(index)
    
    def clear(self) -> None:
        """
        Remove all registered interceptors.
        
        This method clears both request and response interceptor lists,
        effectively resetting the manager to its initial empty state.
        
        Example:
            >>> manager = InterceptorManager()
            >>> manager.use(interceptor1)
            >>> manager.use(interceptor2, is_response=True)
            >>> manager.clear()  # Removes all interceptors
        """
        self.request_interceptors.clear()
        self.response_interceptors.clear()
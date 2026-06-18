"""
AtomHTTP Client Module
----------------------
Main HTTP client class for the AtomHTTP library, providing a comprehensive
interface for making HTTP requests with support for interceptors, progress
tracking, FormData, concurrent requests, and extensive configuration options.

This module contains the AtomHTTP client class which serves as the primary
entry point for all HTTP operations. It provides a clean, axios-like API
with support for all standard HTTP methods, request/response interceptors,
upload/download progress tracking, automatic JSON serialization, and more.
"""

import asyncio
from typing import Dict, Any, Optional, Callable, List, Union
from urllib.parse import urljoin, urlencode, parse_qs
from .core.request import RequestHandler
from .core.response import Response
from .core.config import RequestConfig
from .core.defaults import Defaults
from .core.form_data import FormData
from .interceptors.manager import InterceptorManager
from .errors.http_errors import AtomHTTPError, AtomHTTPRequestError


class AtomHTTP:
    """
    Main HTTP client class providing a comprehensive interface for HTTP requests.
    
    This client is the primary entry point for the AtomHTTP library. It supports:
        - All HTTP methods (GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS)
        - Request and response interceptors
        - Upload and download progress tracking
        - FormData (multipart/form-data) support
        - Automatic JSON serialization/deserialization
        - Base URL configuration
        - Custom headers and query parameters
        - Timeout and redirect configuration
        - Concurrent request helpers (all, spread)
        - Type hints for better IDE support
    
    The client maintains default configuration that applies to all requests,
    which can be overridden on a per-request basis. It also manages a session
    with connection pooling for optimal performance.
    
    Attributes:
        defaults (Defaults): Default configuration for all requests
        interceptors (InterceptorManager): Manager for request/response interceptors
        _request_handler (RequestHandler): Internal handler for request execution
    
    Example:
        >>> client = AtomHTTP({'baseURL': 'https://api.example.com', 'timeout': 30})
        >>> response = await client.get('/users', params={'page': 1})
        >>> print(response.status, response.data)
    """
    
    def __init__(self, config: Optional[Union[RequestConfig, Dict]] = None):
        """
        Initialize a new AtomHTTP client with optional configuration.
        
        Args:
            config (Optional[Union[RequestConfig, Dict]]): Initial configuration
                for the client. Can be a RequestConfig object or a dictionary
                with configuration keys. If None, defaults are used.
        
        Example:
            >>> # Using dictionary
            >>> client = AtomHTTP({'baseURL': 'https://api.example.com', 'timeout': 10})
            >>> 
            >>> # Using RequestConfig object
            >>> config = RequestConfig(baseURL='https://api.example.com', timeout=10)
            >>> client = AtomHTTP(config)
        """
        # Initialize default configuration
        self.defaults = Defaults()
        
        # Apply user configuration if provided
        if config:
            if isinstance(config, dict):
                config_obj = RequestConfig(**config)
            else:
                config_obj = config
            self.defaults.update(config_obj)
        
        # Initialize interceptor manager and request handler
        self.interceptors = InterceptorManager()
        self._request_handler = RequestHandler(self.defaults, self.interceptors)
        self._is_closed = False
    
    async def __aenter__(self):
        """
        Async context manager entry point.
        
        Allows using the client with 'async with' statement for automatic
        resource cleanup and guaranteed session closure.
        
        Returns:
            AtomHTTP: Self instance
        
        Example:
            >>> async with AtomHTTP({'baseURL': 'https://api.example.com'}) as client:
            ...     response = await client.get('/api/users')
            ...     # Session automatically closed on exit
        """
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Async context manager exit point.
        
        Ensures the client is properly closed and all connections are cleaned up
        when exiting the context.
        
        Args:
            exc_type: Exception type if an error occurred
            exc_val: Exception value if an error occurred
            exc_tb: Exception traceback if an error occurred
        """
        await self.close()
        return False
    
    async def request(self, config: Union[RequestConfig, Dict]) -> Response:
        """
        Make an HTTP request with the provided configuration.
        
        This is the core method for making requests. All other HTTP methods
        (get, post, etc.) eventually call this method. It supports full
        configuration including custom adapters, interceptors, and transformers.
        
        Args:
            config (Union[RequestConfig, Dict]): Request configuration. Can be
                a RequestConfig object or a dictionary with configuration keys.
        
        Returns:
            Response: The HTTP response object containing data, status, headers
        
        Example:
            >>> response = await client.request({
            ...     'method': 'POST',
            ...     'url': '/users',
            ...     'data': {'name': 'John'},
            ...     'headers': {'X-Custom': 'value'}
            ... })
        """
        # Convert dictionary to RequestConfig if needed
        if isinstance(config, dict):
            config = RequestConfig(**config)
        
        # Merge with defaults and build full URL
        merged_config = self._merge_config(config)
        final_url = self._build_full_url(merged_config)
        merged_config.url = final_url
        
        # Execute the request through the handler
        return await self._request_handler.execute(merged_config)
    
    async def get(
        self,
        url: str,
        params: Optional[Dict] = None,
        response_type: str = 'json',
        on_download_progress: Optional[Callable] = None,
        **kwargs
    ) -> Response:
        """
        Make an HTTP GET request.
        
        Args:
            url (str): Request URL (absolute or relative to baseURL)
            params (Optional[Dict]): Query parameters to append to URL
            response_type (str): Expected response type ('json', 'text', 'blob',
                                'arraybuffer', 'stream')
            on_download_progress (Optional[Callable]): Callback for download progress
            **kwargs: Additional request configuration options
        
        Returns:
            Response: HTTP response object
        """
        config = RequestConfig(
            url=url,
            method='GET',
            params=params or {},
            responseType=response_type,
            onDownloadProgress=on_download_progress,
            **kwargs
        )
        return await self.request(config)
    
    async def post(
        self,
        url: str,
        data: Any = None,
        response_type: str = 'json',
        on_upload_progress: Optional[Callable] = None,
        on_download_progress: Optional[Callable] = None,
        **kwargs
    ) -> Response:
        """
        Make an HTTP POST request.
        
        Args:
            url (str): Request URL
            data (Any): Request body (dict for JSON, FormData, bytes, etc.)
            response_type (str): Expected response type
            on_upload_progress (Optional[Callable]): Callback for upload progress
            on_download_progress (Optional[Callable]): Callback for download progress
            **kwargs: Additional request configuration options
        
        Returns:
            Response: HTTP response object
        """
        config = RequestConfig(
            url=url,
            method='POST',
            data=data,
            responseType=response_type,
            onUploadProgress=on_upload_progress,
            onDownloadProgress=on_download_progress,
            **kwargs
        )
        return await self.request(config)
    
    async def put(
        self,
        url: str,
        data: Any = None,
        response_type: str = 'json',
        on_upload_progress: Optional[Callable] = None,
        on_download_progress: Optional[Callable] = None,
        **kwargs
    ) -> Response:
        """
        Make an HTTP PUT request.
        
        Args:
            url (str): Request URL
            data (Any): Request body
            response_type (str): Expected response type
            on_upload_progress (Optional[Callable]): Callback for upload progress
            on_download_progress (Optional[Callable]): Callback for download progress
            **kwargs: Additional request configuration options
        
        Returns:
            Response: HTTP response object
        """
        config = RequestConfig(
            url=url,
            method='PUT',
            data=data,
            responseType=response_type,
            onUploadProgress=on_upload_progress,
            onDownloadProgress=on_download_progress,
            **kwargs
        )
        return await self.request(config)
    
    async def patch(
        self,
        url: str,
        data: Any = None,
        response_type: str = 'json',
        on_upload_progress: Optional[Callable] = None,
        on_download_progress: Optional[Callable] = None,
        **kwargs
    ) -> Response:
        """
        Make an HTTP PATCH request.
        
        Args:
            url (str): Request URL
            data (Any): Request body
            response_type (str): Expected response type
            on_upload_progress (Optional[Callable]): Callback for upload progress
            on_download_progress (Optional[Callable]): Callback for download progress
            **kwargs: Additional request configuration options
        
        Returns:
            Response: HTTP response object
        """
        config = RequestConfig(
            url=url,
            method='PATCH',
            data=data,
            responseType=response_type,
            onUploadProgress=on_upload_progress,
            onDownloadProgress=on_download_progress,
            **kwargs
        )
        return await self.request(config)
    
    async def delete(
        self,
        url: str,
        response_type: str = 'json',
        on_download_progress: Optional[Callable] = None,
        **kwargs
    ) -> Response:
        """
        Make an HTTP DELETE request.
        
        Args:
            url (str): Request URL
            response_type (str): Expected response type
            on_download_progress (Optional[Callable]): Callback for download progress
            **kwargs: Additional request configuration options
        
        Returns:
            Response: HTTP response object
        """
        config = RequestConfig(
            url=url,
            method='DELETE',
            responseType=response_type,
            onDownloadProgress=on_download_progress,
            **kwargs
        )
        return await self.request(config)
    
    async def head(
        self,
        url: str,
        response_type: str = 'json',
        on_download_progress: Optional[Callable] = None,
        **kwargs
    ) -> Response:
        """
        Make an HTTP HEAD request.
        
        Args:
            url (str): Request URL
            response_type (str): Expected response type
            on_download_progress (Optional[Callable]): Callback for download progress
            **kwargs: Additional request configuration options
        
        Returns:
            Response: HTTP response object
        """
        config = RequestConfig(
            url=url,
            method='HEAD',
            responseType=response_type,
            onDownloadProgress=on_download_progress,
            **kwargs
        )
        return await self.request(config)
    
    async def options(
        self,
        url: str,
        response_type: str = 'json',
        on_download_progress: Optional[Callable] = None,
        **kwargs
    ) -> Response:
        """
        Make an HTTP OPTIONS request.
        
        Args:
            url (str): Request URL
            response_type (str): Expected response type
            on_download_progress (Optional[Callable]): Callback for download progress
            **kwargs: Additional request configuration options
        
        Returns:
            Response: HTTP response object
        """
        config = RequestConfig(
            url=url,
            method='OPTIONS',
            responseType=response_type,
            onDownloadProgress=on_download_progress,
            **kwargs
        )
        return await self.request(config)
    
    def _merge_config(self, config: RequestConfig) -> RequestConfig:
        """
        Merge user configuration with defaults.
        
        This method combines the provided request configuration with the
        client's default configuration. Headers and params are merged
        (custom values override defaults), while other fields are replaced
        if present.
        
        Args:
            config (RequestConfig): User-provided request configuration
        
        Returns:
            RequestConfig: Merged configuration
        """
        # Start with a copy of defaults
        merged = RequestConfig(**self.defaults.to_dict())
        
        # Merge all attributes from user config
        config_dict = config.to_dict()
        for key, value in config_dict.items():
            if value is not None:
                if key == 'headers' and isinstance(value, dict):
                    if merged.headers is None:
                        merged.headers = {}
                    merged.headers.update(value)
                elif key == 'params' and isinstance(value, dict):
                    if merged.params is None:
                        merged.params = {}
                    merged.params.update(value)
                else:
                    setattr(merged, key, value)
        
        # Ensure baseURL is properly inherited from defaults
        if not merged.baseURL and hasattr(self.defaults, 'baseURL') and self.defaults.baseURL:
            merged.baseURL = self.defaults.baseURL
        
        return merged
    
    def _build_full_url(self, config: RequestConfig) -> str:
        """
        Build a complete URL from baseURL, path, and query parameters.
        
        This method handles:
            - Absolute URLs (ignores baseURL)
            - Relative URLs (combines with baseURL)
            - Query parameter merging (preserves existing query string)
        
        Args:
            config (RequestConfig): Configuration containing URL and parameters
        
        Returns:
            str: Complete URL with base and query parameters
        
        Raises:
            AtomHTTPRequestError: If relative URL is used without baseURL
        """
        url = config.url
        base_url = config.baseURL
        
        # Combine baseURL and relative path
        if base_url and url:
            if url.startswith(('http://', 'https://')):
                final_url = url
            else:
                base = base_url.rstrip('/')
                path = url.lstrip('/')
                final_url = f"{base}/{path}"
        elif base_url and not url:
            final_url = base_url
        elif url:
            if url.startswith(('http://', 'https://')):
                final_url = url
            else:
                raise AtomHTTPRequestError(
                    f"Cannot make request to relative URL '{url}' without baseURL",
                    request=config,
                    config=config
                )
        else:
            raise AtomHTTPRequestError("URL is required", request=config, config=config)
        
        # Append or merge query parameters
        if config.params and len(config.params) > 0:
            if '?' in final_url:
                base_part, existing_params = final_url.split('?', 1)
                existing_dict = parse_qs(existing_params, keep_blank_values=True)
                for key, value in config.params.items():
                    existing_dict[key] = [str(value)]
                flat_params = {}
                for key, values in existing_dict.items():
                    flat_params[key] = values[0] if len(values) == 1 else values
                query_string = urlencode(flat_params, doseq=True)
                final_url = f"{base_part}?{query_string}"
            else:
                query_string = urlencode(config.params)
                final_url = f"{final_url}?{query_string}"
        
        return final_url
    
    @staticmethod
    def all(requests: List[asyncio.Task]) -> asyncio.Future:
        """
        Execute multiple requests concurrently.
        
        This method waits for all provided coroutines/tasks to complete
        and returns their results as a list. Similar to Promise.all() in
        JavaScript.
        
        Args:
            requests (List[asyncio.Task]): List of coroutines or tasks to execute
        
        Returns:
            asyncio.Future: Future that resolves to list of all responses
        
        Example:
            >>> tasks = [
            ...     client.get('/users/1'),
            ...     client.get('/users/2'),
            ...     client.get('/users/3')
            ... ]
            >>> responses = await AtomHTTP.all(tasks)
        """
        return asyncio.gather(*requests)
    
    @staticmethod
    async def spread(callback: Callable, *responses):
        """
        Spread array of responses to callback function arguments.
        
        This method takes a list of responses and passes them as individual
        arguments to the callback function. Similar to axios.spread().
        
        Args:
            callback (Callable): Function that receives individual response arguments
            *responses: Variable number of response objects
        
        Returns:
            Any: Result of the callback function
        
        Example:
            >>> def process(res1, res2, res3):
            ...     return [res1.status, res2.status, res3.status]
            >>> 
            >>> responses = await AtomHTTP.all(tasks)
            >>> statuses = await AtomHTTP.spread(process, *responses)
        """
        return callback(*responses)
    
    def get_uri(self, config: Union[RequestConfig, Dict]) -> str:
        """
        Generate the full URI for a request configuration without executing it.
        
        This method is useful for debugging or when you need to see the
        final URL that would be used for a request.
        
        Args:
            config (Union[RequestConfig, Dict]): Request configuration
        
        Returns:
            str: Full URI with baseURL and query parameters applied
        
        Example:
            >>> uri = client.get_uri({
            ...     'url': '/users',
            ...     'params': {'page': 1, 'limit': 10}
            ... })
            >>> print(uri)
            'https://api.example.com/users?page=1&limit=10'
        """
        # Convert dictionary to RequestConfig if needed
        if isinstance(config, dict):
            config = RequestConfig(**config)
        
        # Merge with defaults and build URL
        if hasattr(self, 'defaults'):
            merged = self._merge_config(config)
        else:
            merged = config
        
        return self._build_full_url(merged)
    
    def is_atomhttp_error(self, error: Exception) -> bool:
        """
        Check if an exception is a AtomHTTP error.
        
        This method is useful for error handling to distinguish between
        AtomHTTP-specific errors and other exceptions.
        
        Args:
            error (Exception): Exception to check
        
        Returns:
            bool: True if the error is a AtomHTTP error, False otherwise
        
        Example:
            >>> try:
            ...     await client.get('https://invalid.com')
            ... except Exception as e:
            ...     if client.is_atomhttp_error(e):
            ...         print(f"AtomHTTP error: {e.code}")
        """
        return isinstance(error, AtomHTTPError)
    
    @staticmethod
    def FormData() -> FormData:
        """
        Create a new FormData instance for multipart/form-data requests.
        
        Returns:
            FormData: New FormData object for building form data with files
        
        Example:
            >>> form = AtomHTTP.FormData()
            >>> form.append('username', 'john')
            >>> form.append('avatar', open('photo.jpg', 'rb'), filename='photo.jpg')
            >>> response = await client.post('/upload', data=form)
        """
        return FormData()
    
    async def close(self) -> None:
        """
        Close the client and clean up resources.
        
        This method should be called when the client is no longer needed
        to properly close connections and release system resources.
        
        Alternatively, use the client with 'async with' statement for automatic
        cleanup:
        
        Example:
            >>> # Manual close
            >>> client = AtomHTTP()
            >>> try:
            ...     response = await client.get('/data')
            ... finally:
            ...     await client.close()
            
            >>> # Automatic close with context manager
            >>> async with AtomHTTP() as client:
            ...     response = await client.get('/data')
        """
        if not self._is_closed:
            if hasattr(self._request_handler, 'default_adapter'):
                await self._request_handler.default_adapter.close()
            self._is_closed = True
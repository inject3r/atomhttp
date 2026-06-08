"""
HTTP Adapter Module
-------------------
Core HTTP transport layer for AtomHTTP client with full feature support including
keep-alive connections, proxy support, progress tracking, and comprehensive
error handling.

This module provides the main HTTPAdapter class that handles all low-level
HTTP communication using aiohttp, along with supporting classes for progress
tracking and mock testing.
"""

import aiohttp
import asyncio
import json
from typing import Optional, Any, Dict, Callable
from urllib.parse import urlencode
from .config import RequestConfig
from .response import Response
from .form_data import FormData
from ..errors.http_errors import (
    AtomHTTPNetworkError, 
    AtomHTTPRequestError, 
    AtomHTTPTimeoutError, 
    AtomHTTPError
)


class BaseAdapter:
    """
    Abstract base class for all HTTP adapters.
    
    Defines the interface that all adapter implementations must follow.
    Adapters are responsible for the actual transport of HTTP requests.
    """
    
    async def send(self, config: RequestConfig) -> Response:
        """
        Execute an HTTP request based on the provided configuration.
        
        Args:
            config (RequestConfig): Request configuration object
            
        Returns:
            Response: The HTTP response
            
        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError
    
    async def close(self):
        """
        Close the adapter and clean up any resources.
        
        This method should be called when the adapter is no longer needed
        to properly release connections and avoid resource leaks.
        """
        pass


class ProgressTracker:
    """
    Track upload and download progress for HTTP requests.
    
    This class provides real-time progress tracking for data transfer operations.
    It works with both upload and download operations, notifying callbacks
    as data is transferred.
    
    Attributes:
        callback (Optional[Callable]): Function called on each progress update
        total (int): Total bytes to transfer (0 if unknown)
        loaded (int): Bytes transferred so far
    """
    
    def __init__(self, callback: Optional[Callable] = None, total: int = 0):
        """
        Initialize a new progress tracker.
        
        Args:
            callback (Optional[Callable]): Function receiving (loaded, total) updates
            total (int): Expected total bytes to transfer
        """
        self.callback = callback
        self.total = total
        self.loaded = 0
    
    def update(self, loaded: int):
        """
        Update the current progress and notify callback if present.
        
        Args:
            loaded (int): Current bytes transferred
        """
        self.loaded = loaded
        if self.callback:
            try:
                self.callback(self.loaded, self.total)
            except Exception:
                # Silently ignore callback errors to prevent breaking the request
                pass
    
    def reset(self):
        """Reset the progress counter to zero."""
        self.loaded = 0


class ProgressReader:
    """
    Wrapper for reading data with automatic progress tracking.
    
    This class wraps a data reader (file, bytes, or any readable object)
    and updates a progress tracker as data is read.
    
    Attributes:
        reader: The underlying data reader object
        progress (ProgressTracker): Progress tracker to update during reads
    """
    
    def __init__(self, reader, progress: ProgressTracker):
        """
        Initialize a progress-tracking reader wrapper.
        
        Args:
            reader: The reader object to wrap (must support read() and async iteration)
            progress (ProgressTracker): Progress tracker to update
        """
        self.reader = reader
        self.progress = progress
    
    async def read(self, size: int = -1):
        """
        Read data and update progress.
        
        Args:
            size (int): Number of bytes to read (-1 for all)
            
        Returns:
            The read data chunk
        """
        chunk = await self.reader.read(size)
        if chunk:
            self.progress.update(self.progress.loaded + len(chunk))
        return chunk
    
    async def __aiter__(self):
        """
        Support async iteration over the reader with progress tracking.
        
        Yields:
            Data chunks as they are read
        """
        async for chunk in self.reader:
            if chunk:
                self.progress.update(self.progress.loaded + len(chunk))
            yield chunk


class HTTPAdapter(BaseAdapter):
    """
    Production HTTP adapter using aiohttp for actual network communication.
    
    This adapter provides the complete HTTP client functionality including:
        - Connection pooling and keep-alive support
        - Proxy configuration
        - Unix socket path support
        - Upload and download progress tracking
        - Automatic decompression (gzip/deflate)
        - Configurable timeouts and redirect limits
        - Comprehensive error handling with typed exceptions
    
    The adapter maintains persistent sessions across requests for optimal
    performance when multiple requests are made.
    
    Attributes:
        _session (Optional[aiohttp.ClientSession]): Persistent HTTP session
        _connector (Optional[aiohttp.TCPConnector]): TCP connector for connection pooling
        _close_lock (asyncio.Lock): Lock for thread-safe session cleanup
    """
    
    def __init__(self):
        """Initialize HTTP adapter with session pooling support."""
        self._session: Optional[aiohttp.ClientSession] = None
        self._connector: Optional[aiohttp.TCPConnector] = None
        self._close_lock = asyncio.Lock()
    
    async def _get_session(self, config: RequestConfig) -> aiohttp.ClientSession:
        """
        Get or create a persistent HTTP session.
        
        Sessions are reused across requests for connection pooling and
        keep-alive benefits. Configuration parameters like keep-alive
        and socket path are applied when creating new sessions.
        
        Args:
            config (RequestConfig): Request configuration containing connection settings
            
        Returns:
            aiohttp.ClientSession: Active HTTP session
        """
        async with self._close_lock:
            if self._session is None or self._session.closed:
                # Extract connection configuration from request
                keep_alive = getattr(config, 'keepAlive', True)
                socket_path = getattr(config, 'socketPath', None)
                
                # Configure TCP connector with appropriate settings
                connector_kwargs = {
                    'keepalive_timeout': 30 if keep_alive else 0,
                    'force_close': not keep_alive,
                    'enable_cleanup_closed': True,
                }
                
                # Add Unix socket support if specified
                if socket_path:
                    connector_kwargs['socket_path'] = socket_path
                
                # Clean up existing connector if present
                if self._connector and not self._connector.closed:
                    await self._connector.close()
                
                # Create new connector and session
                self._connector = aiohttp.TCPConnector(**connector_kwargs)
                self._session = aiohttp.ClientSession(
                    connector=self._connector,
                    trust_env=True  # Respect HTTP_PROXY environment variables
                )
        
        return self._session
    
    async def send(self, config: RequestConfig) -> Response:
        """
        Execute HTTP request with full feature support.
        
        This method handles the complete request lifecycle:
            1. Session acquisition
            2. Request data preparation (JSON, FormData, bytes, etc.)
            3. Header configuration and auto-headers
            4. Proxy routing (if configured)
            5. Progress tracking setup
            6. Request execution
            7. Response processing (JSON, text, blob, arraybuffer, stream)
            8. Status validation
            9. Error transformation to AtomHTTP error types
        
        Args:
            config (RequestConfig): Complete request configuration
            
        Returns:
            Response: Processed response object
            
        Raises:
            AtomHTTPTimeoutError: Request exceeded timeout
            AtomHTTPNetworkError: Network connectivity issues
            AtomHTTPRequestError: Bad request or unexpected response
        """
        # Convert timeout to seconds and create aiohttp timeout object
        timeout_seconds = float(config.timeout) if config.timeout else 30.0
        timeout = aiohttp.ClientTimeout(total=timeout_seconds)
        
        # Get or create persistent session
        session = await self._get_session(config)
        
        # Initialize request data variables
        data = None
        json_data = None
        content_type = None
        upload_progress = None
        
        # Process request data based on type
        if config.data is not None:
            # Handle FormData (multipart/form-data)
            if isinstance(config.data, FormData):
                data, boundary = config.data.to_multipart()
                content_type = f"multipart/form-data; boundary={boundary}"
                
                # Setup upload progress tracking for FormData
                if config.onUploadProgress:
                    upload_progress = ProgressTracker(config.onUploadProgress, len(data) if data else 0)
                    data = ProgressReader(type('Reader', (), {'read': lambda s, d=data: d})(), upload_progress)
            
            # Handle dict or list as JSON by default
            elif isinstance(config.data, (dict, list)):
                json_data = config.data
                content_type = 'application/json'
                
                # Setup upload progress for JSON
                if config.onUploadProgress:
                    json_str = json.dumps(json_data)
                    upload_progress = ProgressTracker(config.onUploadProgress, len(json_str))
                    json_data = json_str
            
            # Handle string data
            elif isinstance(config.data, str):
                stripped = config.data.strip()
                # Check if string is JSON-like
                if stripped.startswith('{') or stripped.startswith('['):
                    try:
                        json_data = json.loads(config.data)
                        content_type = 'application/json'
                        if config.onUploadProgress:
                            upload_progress = ProgressTracker(config.onUploadProgress, len(config.data))
                            json_data = config.data
                    except json.JSONDecodeError:
                        # Not valid JSON, treat as plain text
                        data = config.data
                        if config.onUploadProgress:
                            upload_progress = ProgressTracker(config.onUploadProgress, len(config.data))
                            data = config.data
                else:
                    # Plain text data
                    data = config.data
                    if config.onUploadProgress:
                        upload_progress = ProgressTracker(config.onUploadProgress, len(config.data))
                        data = config.data
            
            # Handle bytes data
            elif isinstance(config.data, bytes):
                data = config.data
                if config.onUploadProgress:
                    upload_progress = ProgressTracker(config.onUploadProgress, len(config.data))
                    data = config.data
            
            # Convert any other type to string
            else:
                data = str(config.data)
                if config.onUploadProgress:
                    upload_progress = ProgressTracker(config.onUploadProgress, len(data))
        
        # Prepare request headers
        headers = {}
        if config.headers:
            headers.update(config.headers)
        
        # Set Content-Type if not already specified
        if content_type and 'Content-Type' not in headers:
            headers['Content-Type'] = content_type
        
        # Add standard X-Requested-With header (identifies AJAX requests)
        headers['X-Requested-With'] = 'XMLHttpRequest'
        
        # Build full URL including query parameters
        full_url = config.url
        if config.params and len(config.params) > 0:
            if '?' in full_url:
                full_url = f"{full_url}&{urlencode(config.params)}"
            else:
                full_url = f"{full_url}?{urlencode(config.params)}"
        
        # Prepare request arguments
        request_kwargs = {
            'method': config.method,
            'url': full_url,
            'headers': headers,
            'timeout': timeout,
            'max_redirects': config.maxRedirects,
            'ssl': True,
        }
        
        # Add request body (either JSON or raw data)
        if json_data is not None:
            request_kwargs['json'] = json_data
        elif data is not None:
            request_kwargs['data'] = data
        
        # Configure proxy if specified
        if config.proxy:
            proxy_url = config.proxy.get('host')
            if proxy_url:
                request_kwargs['proxy'] = proxy_url
                if 'auth' in config.proxy:
                    auth = config.proxy['auth']
                    if auth.get('username') and auth.get('password'):
                        request_kwargs['proxy_auth'] = aiohttp.BasicAuth(
                            auth['username'], auth['password']
                        )
        
        # Enable/disable response decompression
        if hasattr(config, 'decompress'):
            request_kwargs['compress'] = config.decompress
        
        try:
            # Initialize upload progress (0%)
            if upload_progress:
                upload_progress.update(0)
            
            # Execute the HTTP request
            response = await session.request(**request_kwargs)
            
            # Mark upload as complete
            if upload_progress and upload_progress.total > 0:
                upload_progress.update(upload_progress.total)
            
            # Validate response content length against configured maximum
            if hasattr(config, 'maxContentLength') and config.maxContentLength > 0:
                content_length = response.content_length
                if content_length and content_length > config.maxContentLength:
                    response.close()
                    raise AtomHTTPRequestError(
                        f"Response content length {content_length} exceeds maxContentLength {config.maxContentLength}",
                        request=config, config=config
                    )
            
            # Determine response type (json, text, blob, arraybuffer, stream)
            response_type = getattr(config, 'responseType', 'json')
            
            # Setup download progress tracking if callback provided
            if config.onDownloadProgress:
                content_length = response.content_length
                download_progress = ProgressTracker(config.onDownloadProgress, content_length or 0)
                
                # Create wrapper response that tracks download progress
                class ProgressResponse:
                    def __init__(self, original, progress, response_type):
                        self.original = original
                        self.progress = progress
                        self.status = original.status
                        self.reason = original.reason
                        self.headers = dict(original.headers)
                        self._content = None
                        self.response_type = response_type
                    
                    async def _read_with_progress(self):
                        """Read all data while tracking progress."""
                        if self._content is not None:
                            return self._content
                        
                        data = bytearray()
                        async for chunk in self.original.content.iter_chunks():
                            chunk_data = chunk[0]
                            if chunk_data:
                                data.extend(chunk_data)
                                self.progress.update(len(data))
                        
                        self._content = bytes(data)
                        return self._content
                    
                    async def json(self):
                        """Parse response as JSON."""
                        data = await self._read_with_progress()
                        return json.loads(data.decode('utf-8'))
                    
                    async def text(self):
                        """Return response as text."""
                        data = await self._read_with_progress()
                        return data.decode('utf-8')
                    
                    async def read(self):
                        """Return raw bytes."""
                        return await self._read_with_progress()
                    
                    async def __aenter__(self):
                        return self
                    
                    async def __aexit__(self, *args):
                        pass
                
                response = ProgressResponse(response, download_progress, response_type)
            
            # Parse response body based on specified type
            if response_type == 'json':
                try:
                    if hasattr(response, 'json'):
                        response_data = await response.json()
                    else:
                        response_data = await response.json()
                except aiohttp.ContentTypeError:
                    # Response isn't JSON, try to parse anyway or return as text
                    text = await response.text()
                    try:
                        response_data = json.loads(text)
                    except json.JSONDecodeError:
                        response_data = text
                except Exception:
                    response_data = await response.text()
            
            elif response_type == 'text':
                if hasattr(response, 'text'):
                    response_data = await response.text()
                else:
                    response_data = await response.text()
            
            elif response_type == 'blob':
                # Return as raw bytes
                if hasattr(response, 'read'):
                    response_data = await response.read()
                else:
                    response_data = await response.read()
            
            elif response_type == 'arraybuffer':
                # Return as raw bytes (alias for blob)
                if hasattr(response, 'read'):
                    response_data = await response.read()
                else:
                    response_data = await response.read()
            
            elif response_type == 'stream':
                # Return the raw stream for large data processing
                if hasattr(response, 'content'):
                    response_data = response.content
                else:
                    response_data = response.content
            
            else:
                # Default to text
                response_data = await response.text()
            
            # Extract response headers
            if hasattr(response, 'headers'):
                response_headers = dict(response.headers)
            else:
                response_headers = {}
            
            # Validate HTTP status code if custom validator provided
            if config.validateStatus:
                if not config.validateStatus(response.status):
                    error = AtomHTTPRequestError(
                        f"Request failed with status code {response.status}",
                        request=config, config=config, response=response
                    )
                    error.code = f"ERR_BAD_{response.status}"
                    error.response = response
                    raise error
            
            # Return wrapped response object
            return Response(
                data=response_data,
                status=response.status,
                status_text=response.reason,
                headers=response_headers,
                config=config,
                request=config
            )
            
        except asyncio.TimeoutError:
            # Convert asyncio timeout to AtomHTTP timeout error
            error = AtomHTTPTimeoutError(f"Request timeout after {timeout_seconds}s", config=config)
            error.code = 'ECONNABORTED'
            raise error
            
        except aiohttp.ClientConnectorError as e:
            # Network connection issues (DNS failure, refused connection, etc.)
            error = AtomHTTPNetworkError(f"Connection error: {str(e)}", config=config)
            error.code = 'ERR_NETWORK'
            raise error
            
        except aiohttp.ClientResponseError as e:
            # HTTP response error (4xx, 5xx) that wasn't caught by validateStatus
            if config.validateStatus and not config.validateStatus(e.status):
                raise
            error = AtomHTTPRequestError(f"Response error: {str(e)}", request=config, config=config)
            error.code = f"ERR_BAD_{e.status}"
            error.response = e
            raise error
            
        except aiohttp.ClientError as e:
            # Generic aiohttp client error
            error = AtomHTTPNetworkError(f"Network error: {str(e)}", config=config)
            error.code = 'ERR_NETWORK'
            raise error
            
        except AtomHTTPError:
            # Re-raise AtomHTTP errors without modification
            raise
            
        except Exception as e:
            # Convert any other exception to AtomHTTP request error
            error = AtomHTTPRequestError(str(e), request=config, config=config)
            error.code = 'ERR_BAD_REQUEST'
            raise error
    
    async def close(self):
        """
        Close the HTTP adapter and release all resources.
        
        This method properly closes the underlying aiohttp session and
        TCP connector, ensuring all connections are properly cleaned up
        to prevent resource leaks.
        """
        async with self._close_lock:
            try:
                if self._session and not self._session.closed:
                    await self._session.close()
                if self._connector and not self._connector.closed:
                    await self._connector.close()
            except Exception:
                # Silently ignore cleanup errors
                pass


class MockAdapter(BaseAdapter):
    """
    Mock adapter for testing and development without real network calls.
    
    This adapter stores predefined responses and returns them when matching
    requests are made. It enables isolated testing of code that depends on
    HTTP responses without requiring external services or network connectivity.
    
    Features:
        - Register mock responses for specific HTTP methods and URLs
        - Customizable response data, status codes, and headers
        - Automatic 404 for unregistered endpoints
        - Case-insensitive method matching (GET/get/Get all work)
        - Clear all mocks with clear() method
    
    Attributes:
        _responses (Dict[str, Dict]): Internal storage of registered mock responses
    """
    
    def __init__(self):
        """Initialize empty mock adapter with no registered responses."""
        self._responses: Dict[str, Dict] = {}
    
    def on(self, method: str, url: str, response_data: Any, status: int = 200, headers: Dict = None):
        """
        Register a mock response for a specific HTTP method and URL.
        
        When a request matches the registered method and URL, the specified
        response will be returned instead of making a network request.
        
        Args:
            method (str): HTTP method (GET, POST, PUT, DELETE, etc.)
            url (str): Full URL that this mock should respond to
            response_data (Any): Data to return as the response body
            status (int): HTTP status code (default: 200)
            headers (Dict, optional): Custom response headers
        """
        # Use uppercase for case-insensitive method matching
        key = f"{method.upper()}:{url}"
        self._responses[key] = {
            'data': response_data,
            'status': status,
            'status_text': 'OK' if status == 200 else 'Error',
            'headers': headers or {}
        }
    
    async def send(self, config: RequestConfig) -> Response:
        """
        Return a mock response for the request if registered.
        
        Args:
            config (RequestConfig): Request configuration containing method and URL
            
        Returns:
            Response: Registered mock response or 404 error if not found
        """
        # Build lookup key with uppercase method for case-insensitive matching
        key = f"{config.method.upper()}:{config.url}"
        
        if key in self._responses:
            mock = self._responses[key]
            return Response(
                data=mock['data'],
                status=mock['status'],
                status_text=mock['status_text'],
                headers=mock['headers'],
                config=config,
                request=config
            )
        else:
            # Return 404 for unregistered endpoints
            return Response(
                data={'error': f'No mock found for {key}'},
                status=404,
                status_text='Not Found',
                headers={},
                config=config,
                request=config
            )
    
    async def close(self):
        """
        Close the mock adapter.
        
        Mock adapter has no resources to clean up, but this method exists
        for interface compliance with BaseAdapter.
        """
        pass
    
    def clear(self):
        """
        Clear all registered mock responses.
        
        This method removes all previously registered mocks, allowing the
        adapter to be reused for a different test scenario.
        """
        self._responses.clear()
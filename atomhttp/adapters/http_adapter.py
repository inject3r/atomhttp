"""
HTTP Adapter Module with Connection Pooling and Retry Support
--------------------------------------------------------------
This module provides the HTTP adapter for making asynchronous HTTP requests
using aiohttp with persistent connection pooling, automatic retries with
exponential backoff, SSL verification control, and comprehensive error handling.

The HTTPAdapter is the default transport layer for the AtomHTTP client,
responsible for low-level HTTP communication including session management,
connection pooling, timeout handling, proxy configuration, and response processing.
"""

import aiohttp
import asyncio
import time
from typing import Optional, Dict, Any
from ..core.config import RequestConfig
from ..core.response import Response
from ..errors.http_errors import (
    AtomHTTPNetworkError,
    AtomHTTPTimeoutError,
    AtomHTTPError
)


class HTTPAdapter:
    """
    Production HTTP adapter with connection pooling and retry support.
    
    This adapter provides optimized HTTP communication with:
        - Persistent session with connection pooling (keep-alive)
        - Automatic retries with exponential backoff
        - SSL/TLS verification control
        - Proxy support
        - Unix socket support
        - Comprehensive timeout management
        - Configurable connector settings (connection limits, pool size)
    
    Attributes:
        _session (Optional[aiohttp.ClientSession]): Persistent HTTP session
        _connector (Optional[aiohttp.TCPConnector]): TCP connector for pooling
        _ssl_context (Optional[aiohttp.TCPConnector]): SSL context for verification
        proxy (Optional[str]): Proxy server URL
        pool_size (int): Connection pool size per host (default: 100)
        max_per_host (int): Maximum connections per host (default: 30)
    """
    
    def __init__(
        self,
        proxy: Optional[str] = None,
        pool_size: int = 100,
        max_per_host: int = 30,
        socket_path: Optional[str] = None
    ):
        """
        Initialize HTTP adapter with connection pooling.
        
        Args:
            proxy (Optional[str]): Proxy server URL
            pool_size (int): Total connection pool size (default: 100)
            max_per_host (int): Max connections per host (default: 30)
            socket_path (Optional[str]): Unix socket path for connection
        """
        self.proxy = proxy
        self.pool_size = pool_size
        self.max_per_host = max_per_host
        self.socket_path = socket_path
        
        self._session: Optional[aiohttp.ClientSession] = None
        self._connector: Optional[aiohttp.TCPConnector] = None
        self._ssl_context: Optional[Any] = None
        self._close_lock = asyncio.Lock()
    
    async def _initialize_session(self, config: RequestConfig):
        """
        Initialize or get existing persistent session.
        
        Creates a single persistent session with proper connection pooling
        configuration. The session is reused across all requests.
        
        Args:
            config (RequestConfig): Request configuration for SSL settings
        """
        if self._session is not None:
            return
        
        # Create connector with connection pooling
        connector = aiohttp.TCPConnector(
            limit=self.pool_size,
            limit_per_host=self.max_per_host,
            ttl_dns_cache=300,  # 5 minutes DNS cache
            use_dns_cache=True,
            enable_cleanup_closed=True,
            force_close=False  # Keep connections alive
        )
        
        # Create SSL context based on verify setting
        if hasattr(config, 'verify') and not config.verify:
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            connector = aiohttp.TCPConnector(
                limit=self.pool_size,
                limit_per_host=self.max_per_host,
                ttl_dns_cache=300,
                ssl=ssl_context
            )
        
        self._connector = connector
        self._session = aiohttp.ClientSession(
            connector=connector,
            trust_env=True  # Use environment proxy settings
        )
    
    async def close(self):
        """
        Close and cleanup the session and connector.
        
        Should be called when the adapter is no longer needed to properly
        release all connections and cleanup resources.
        """
        async with self._close_lock:
            if self._session:
                await self._session.close()
                # Give some time for connections to close
                await asyncio.sleep(0.25)
                self._session = None
            
            if self._connector:
                await self._connector.close()
                self._connector = None
    
    async def _get_retry_config(self, config: RequestConfig) -> Dict[str, Any]:
        """
        Extract retry configuration with sensible defaults.
        
        Args:
            config (RequestConfig): Request configuration
            
        Returns:
            Dict: Retry configuration
        """
        default_retry = {
            'max_retries': 3,
            'backoff_factor': 0.3,
            'status_forcelist': [408, 429, 500, 502, 503, 504],
            'method_whitelist': ['GET', 'HEAD', 'OPTIONS', 'DELETE']
        }
        
        if hasattr(config, 'retryConfig') and config.retryConfig:
            default_retry.update(config.retryConfig)
        
        return default_retry
    
    async def send(self, config: RequestConfig) -> Response:
        """
        Execute an HTTP request with automatic retries and connection pooling.
        
        This method implements the full request lifecycle with:
            - Persistent session reuse (connection pooling)
            - Automatic retries with exponential backoff
            - SSL verification control
            - Proxy support
            - Comprehensive error handling
        
        Args:
            config (RequestConfig): Complete request configuration
        
        Returns:
            Response: Wrapped HTTP response
        
        Raises:
            AtomHTTPTimeoutError: Request timeout
            AtomHTTPNetworkError: Network error
            AtomHTTPError: Other HTTP errors
        """
        # Initialize session (only once)
        await self._initialize_session(config)
        
        # Get retry configuration
        retry_config = await self._get_retry_config(config)
        max_retries = retry_config.get('max_retries', 3)
        backoff_factor = retry_config.get('backoff_factor', 0.3)
        status_forcelist = retry_config.get('status_forcelist', [408, 429, 500, 502, 503, 504])
        
        # Prepare request parameters
        timeout = aiohttp.ClientTimeout(total=config.timeout)
        
        # SSL verification
        ssl_context = None
        if hasattr(config, 'verify') and not config.verify:
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
        
        # Retry loop with exponential backoff
        last_error = None
        for attempt in range(max_retries + 1):
            try:
                # Make the actual request
                async with self._session.request(
                    method=config.method,
                    url=config.url,
                    headers=config.headers,
                    params=config.params,
                    data=config.data,
                    timeout=timeout,
                    max_redirects=config.maxRedirects,
                    proxy=self.proxy,
                    ssl=ssl_context if ssl_context else None,
                    allow_redirects=config.maxRedirects > 0
                ) as response:
                    # Read response body
                    try:
                        if config.responseType == 'json':
                            data = await response.json()
                        elif config.responseType == 'text':
                            data = await response.text()
                        elif config.responseType == 'bytes':
                            data = await response.read()
                        else:
                            data = await response.text()
                    except Exception as e:
                        data = None
                        if config.responseType == 'json':
                            # Try to parse as text if JSON fails
                            try:
                                data = await response.text()
                            except:
                                pass
                    
                    # Check if we should retry based on status code
                    if response.status in status_forcelist and attempt < max_retries:
                        # Calculate backoff time with jitter
                        backoff_time = backoff_factor * (2 ** attempt)
                        jitter = backoff_time * 0.1
                        import random
                        sleep_time = backoff_time + (random.random() * jitter)
                        await asyncio.sleep(sleep_time)
                        continue
                    
                    # Success or non-retryable status
                    return Response(
                        data=data,
                        status=response.status,
                        status_text=response.reason or '',
                        headers=dict(response.headers),
                        config=config,
                        request=config
                    )
                
            except asyncio.TimeoutError as e:
                last_error = AtomHTTPTimeoutError(
                    f"Request timeout after {config.timeout} seconds (attempt {attempt + 1}/{max_retries + 1})",
                    config=config
                )
                
                # Retry on timeout if we have attempts left
                if attempt < max_retries:
                    backoff_time = backoff_factor * (2 ** attempt)
                    jitter = backoff_time * 0.1
                    import random
                    sleep_time = backoff_time + (random.random() * jitter)
                    await asyncio.sleep(sleep_time)
                    continue
                else:
                    raise last_error
            
            except (aiohttp.ClientConnectorError, aiohttp.ClientSSLError) as e:
                last_error = AtomHTTPNetworkError(
                    f"Network error: {str(e)} (attempt {attempt + 1}/{max_retries + 1})",
                    config=config
                )
                
                # Retry on network errors
                if attempt < max_retries:
                    backoff_time = backoff_factor * (2 ** attempt)
                    jitter = backoff_time * 0.1
                    import random
                    sleep_time = backoff_time + (random.random() * jitter)
                    await asyncio.sleep(sleep_time)
                    continue
                else:
                    raise last_error
            
            except Exception as e:
                last_error = AtomHTTPError(
                    f"Request failed: {str(e)} (attempt {attempt + 1}/{max_retries + 1})",
                    config=config
                )
                
                # Don't retry on unexpected errors
                raise last_error
        
        # Should not reach here, but just in case
        if last_error:
            raise last_error
        
        raise AtomHTTPError("Request failed after all retries", config=config)

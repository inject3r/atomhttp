"""
Request Configuration Module
----------------------------
Defines the configuration data class for HTTP requests in AtomHTTP.

This module provides the RequestConfig dataclass which holds all configuration
parameters for an HTTP request, similar to axios configuration objects.
It supports timeouts, headers, authentication, proxies, redirects, data
transformation, and various other request settings.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, Callable, Union
from datetime import timedelta


@dataclass
class RequestConfig:
    """
    Configuration object for HTTP requests, inspired by axios config.
    
    This dataclass holds all parameters needed to configure and execute
    an HTTP request. It provides a flexible and extensible way to specify
    request options including URL, method, headers, data, timeouts,
    authentication, proxy settings, and response handling.
    
    Attributes:
        url (str): Target URL for the request. Can be absolute or relative
                  when used with baseURL.
        
        method (str): HTTP method (GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS).
                     Defaults to 'GET'.
        
        baseURL (str): Base URL prepended to relative URLs. Useful for API clients.
        
        headers (Dict[str, str]): Custom HTTP headers to send with the request.
                                 These override default headers.
        
        params (Dict[str, Any]): Query parameters to append to the URL.
                                Automatically URL-encoded.
        
        data (Any): Request body data. Can be dict (JSON), str, bytes,
                   FormData, or file-like object.
        
        timeout (Union[int, float, timedelta]): Request timeout in seconds.
                                               Can be integer, float, or timedelta.
                                               Defaults to 30 seconds.
        
        withCredentials (bool): Whether to send cookies with cross-site requests.
                               Defaults to False.
        
        auth (Optional[Dict[str, str]]): Basic authentication credentials.
                                        Format: {'username': 'user', 'password': 'pass'}
        
        proxy (Optional[Dict[str, Any]]): Proxy server configuration.
                                         Format: {'host': 'http://proxy:8080', 'auth': {...}}
        
        maxRedirects (int): Maximum number of redirects to follow. Defaults to 5.
        
        maxContentLength (int): Maximum allowed response body size in bytes.
                               -1 means no limit. Defaults to -1.
        
        maxBodyLength (int): Maximum allowed request body size in bytes.
                            -1 means no limit. Defaults to -1.
        
        transformRequest (Optional[Callable]): Function to transform request data
                                              before sending.
        
        transformResponse (Optional[Callable]): Function to transform response data
                                               before returning.
        
        responseType (str): Expected response type. Options: 'json', 'text',
                           'blob', 'arraybuffer', 'stream'. Defaults to 'json'.
        
        xsrfCookieName (str): Name of the cookie containing the XSRF token.
                             Defaults to 'XSRF-TOKEN'.
        
        xsrfHeaderName (str): Name of the header to send XSRF token in.
                             Defaults to 'X-XSRF-TOKEN'.
        
        onUploadProgress (Optional[Callable]): Callback for upload progress.
                                              Receives (loaded, total) arguments.
        
        onDownloadProgress (Optional[Callable]): Callback for download progress.
                                                Receives (loaded, total) arguments.
        
        socketPath (Optional[str]): Unix domain socket path for connection.
                                   Example: '/var/run/docker.sock'
        
        keepAlive (bool): Enable HTTP keep-alive connections. Defaults to True.
        
        decompress (bool): Automatically decompress gzip/deflate responses.
                          Defaults to True.
        
        validateStatus (Optional[Callable]): Function to determine if status code
                                            should resolve or reject. Receives status.
        
        adapter (Optional[Any]): Custom HTTP adapter for request execution.
        
        transitional (Dict[str, bool]): Transitional configuration options for
                                       backward compatibility.
    """
    
    # Core request parameters
    url: str = ''
    method: str = 'GET'
    baseURL: str = ''
    
    # Headers and parameters
    headers: Dict[str, str] = field(default_factory=dict)
    params: Dict[str, Any] = field(default_factory=dict)
    data: Any = None
    
    # Timing and connection settings
    timeout: Union[int, float, timedelta] = 30
    withCredentials: bool = False
    
    # Authentication and proxy
    auth: Optional[Dict[str, str]] = None
    proxy: Optional[Dict[str, Any]] = None
    
    # Request limits and redirects
    maxRedirects: int = 5
    maxContentLength: int = -1
    maxBodyLength: int = -1
    
    # Data transformation
    transformRequest: Optional[Callable] = None
    transformResponse: Optional[Callable] = None
    
    # Response handling
    responseType: str = 'json'
    
    # CSRF protection
    xsrfCookieName: str = 'XSRF-TOKEN'
    xsrfHeaderName: str = 'X-XSRF-TOKEN'
    
    # Progress tracking
    onUploadProgress: Optional[Callable] = None
    onDownloadProgress: Optional[Callable] = None
    
    # Low-level connection options
    socketPath: Optional[str] = None
    keepAlive: bool = True
    decompress: bool = True
    
    # Status validation
    validateStatus: Optional[Callable] = None
    
    # Custom adapter
    adapter: Optional[Any] = None
    
    # Transitional options for backward compatibility
    transitional: Dict[str, bool] = field(default_factory=lambda: {
        'silentJSONParsing': True,
        'forcedJSONParsing': True,
        'clarifyTimeoutError': False
    })
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the configuration to a dictionary, omitting None values.
        
        This method serializes the RequestConfig object to a dictionary
        suitable for JSON serialization or for passing to other functions.
        Special handling is applied to timedelta timeout values, converting
        them to seconds.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the config with all
                           non-None values included.
        
        Example:
            >>> config = RequestConfig(url='/api', timeout=timedelta(seconds=5))
            >>> config.to_dict()
            {'url': '/api', 'timeout': 5.0}
        """
        # Convert dataclass to dictionary
        data = asdict(self)
        
        # Convert timedelta to seconds if present
        if isinstance(self.timeout, timedelta):
            data['timeout'] = self.timeout.total_seconds()
        
        # Remove None values to keep the dictionary clean
        return {k: v for k, v in data.items() if v is not None}
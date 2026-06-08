"""
URL and Header Utilities
------------------------
Helper functions for URL construction, header merging, and parameter parsing.

This module provides utility functions for common operations needed in HTTP
client operations, including merging headers, building URLs with query
parameters, and parsing parameter dictionaries.
"""

from typing import Dict, Any, Optional
from urllib.parse import urlencode, urljoin


def merge_headers(default: Dict[str, str], custom: Dict[str, str]) -> Dict[str, str]:
    """
    Merge default headers with custom headers.
    
    Custom headers take precedence over default headers when keys conflict.
    This function creates a new dictionary rather than modifying the originals.
    
    Args:
        default (Dict[str, str]): Default headers (base values)
        custom (Dict[str, str]): Custom headers that override defaults
    
    Returns:
        Dict[str, str]: Merged headers dictionary where custom headers
                       override default headers on key conflicts
    
    Example:
        >>> default = {'Accept': 'application/json', 'User-Agent': 'client/1.0'}
        >>> custom = {'Authorization': 'Bearer token', 'Accept': 'text/plain'}
        >>> merged = merge_headers(default, custom)
        >>> print(merged)
        {'Accept': 'text/plain', 'User-Agent': 'client/1.0', 'Authorization': 'Bearer token'}
    """
    merged = default.copy()
    merged.update(custom)
    return merged


def build_url(
    base_url: str,
    path: str,
    params: Optional[Dict[str, Any]] = None
) -> str:
    """
    Build a complete URL by combining base URL, path, and query parameters.
    
    This function handles both absolute and relative paths. If the path
    already contains a protocol (http:// or https://), the base_url is
    ignored and the path is used as the full URL.
    
    Args:
        base_url (str): Base URL (e.g., 'https://api.example.com')
        path (str): URL path (e.g., '/users' or 'https://other.com/api')
        params (Optional[Dict[str, Any]]): Query parameters to append
        
    Returns:
        str: Complete URL with path and query parameters properly encoded
    
    Example:
        >>> build_url('https://api.example.com', '/users', {'page': 1, 'limit': 10})
        'https://api.example.com/users?page=1&limit=10'
        
        >>> build_url('https://api.example.com', 'https://other.com/api')
        'https://other.com/api'
        
        >>> build_url('https://api.example.com', '/search', {'q': 'python http'})
        'https://api.example.com/search?q=python%20http'
    """
    # If path is absolute (has protocol), use it as the full URL
    if path.startswith(('http://', 'https://')):
        url = path
    else:
        # Combine base URL and relative path
        url = urljoin(base_url, path)
    
    # Append query parameters if provided
    if params:
        query_string = urlencode(params)
        # Add parameters as query string (appending if already exists)
        if '?' not in url:
            url = f"{url}?{query_string}"
        else:
            url = f"{url}&{query_string}"
    
    return url


def parse_params(params: Dict[str, Any]) -> Dict[str, str]:
    """
    Parse and convert parameter dictionary to string-keyed dictionary.
    
    This function filters out None values and converts all values to strings,
    preparing them for URL encoding or other string-based operations.
    
    Args:
        params (Dict[str, Any]): Input parameters with any value types
        
    Returns:
        Dict[str, str]: Filtered dictionary with None values removed and
                       all values converted to strings
    
    Example:
        >>> params = {'page': 1, 'limit': 10, 'sort': None, 'active': True}
        >>> parsed = parse_params(params)
        >>> print(parsed)
        {'page': '1', 'limit': '10', 'active': 'True'}
    """
    return {k: str(v) for k, v in params.items() if v is not None}
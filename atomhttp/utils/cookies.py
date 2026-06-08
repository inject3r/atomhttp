"""
Cookie Manager Module
---------------------
Provides HTTP cookie handling for the AtomHTTP client.

This module contains the CookieManager class which manages HTTP cookies
for client sessions. It supports setting, retrieving, and formatting cookies
for requests, as well as parsing cookies from server responses.
"""

from http.cookies import SimpleCookie
from typing import Dict, Optional


class CookieManager:
    """
    Manage HTTP cookies for client sessions.
    
    This class wraps Python's SimpleCookie to provide a convenient interface
    for cookie management in HTTP client operations. It supports:
        - Setting cookies with additional attributes (domain, path, expires, etc.)
        - Retrieving cookie values by name
        - Generating Cookie header values for requests
        - Parsing Set-Cookie headers from responses
    
    The manager maintains cookies across requests when the same client
    instance is used, enabling session persistence.
    
    Attributes:
        _cookies (SimpleCookie): Internal SimpleCookie object storing all cookies
    """
    
    def __init__(self):
        """
        Initialize an empty cookie manager.
        
        No cookies are present initially. Cookies can be added via set_cookie()
        or loaded from response headers via load_from_response().
        """
        self._cookies = SimpleCookie()
    
    def set_cookie(self, name: str, value: str, **kwargs) -> None:
        """
        Set a cookie with optional attributes.
        
        This method sets a cookie value and optionally adds attributes such
        as domain, path, expires, secure, httponly, etc.
        
        Args:
            name (str): Cookie name
            value (str): Cookie value
            **kwargs: Optional cookie attributes (domain, path, expires, max-age,
                     secure, httponly, samesite, etc.)
        
        Example:
            >>> manager = CookieManager()
            >>> manager.set_cookie('session', 'abc123', domain='.example.com', path='/')
            >>> manager.set_cookie('user', 'john', max_age=3600, secure=True)
        """
        self._cookies[name] = value
        for key, val in kwargs.items():
            self._cookies[name][key] = val
    
    def get_cookie(self, name: str) -> Optional[str]:
        """
        Get the value of a cookie by name.
        
        Args:
            name (str): Name of the cookie to retrieve
            
        Returns:
            Optional[str]: Cookie value if found, None otherwise
        
        Example:
            >>> manager = CookieManager()
            >>> manager.set_cookie('session', 'abc123')
            >>> value = manager.get_cookie('session')
            >>> print(value)
            'abc123'
        """
        if name in self._cookies:
            return self._cookies[name].value
        return None
    
    def get_header(self) -> str:
        """
        Generate the Cookie header value for HTTP requests.
        
        This method formats all stored cookies into a string suitable for
        the Cookie header. Cookies are formatted as "name=value" pairs
        separated by semicolons.
        
        Returns:
            str: Cookie header value (empty string if no cookies)
        
        Example:
            >>> manager = CookieManager()
            >>> manager.set_cookie('session', 'abc123')
            >>> manager.set_cookie('user', 'john')
            >>> print(manager.get_header())
            'session=abc123; user=john'
        """
        return '; '.join([f"{k}={v.value}" for k, v in self._cookies.items()])
    
    def load_from_response(self, header: str) -> None:
        """
        Parse and load cookies from a Set-Cookie response header.
        
        This method processes Set-Cookie headers from server responses and
        adds the cookies to the manager. Existing cookies with the same
        name may be overwritten according to cookie precedence rules.
        
        Args:
            header (str): The Set-Cookie header value from an HTTP response
        
        Example:
            >>> manager = CookieManager()
            >>> set_cookie = "session=abc123; Path=/; HttpOnly"
            >>> manager.load_from_response(set_cookie)
            >>> print(manager.get_cookie('session'))
            'abc123'
        
        Note:
            This method uses SimpleCookie.load() which parses the cookie
            string according to RFC 6265. Multiple cookies in a single
            header are supported as per the standard.
        """
        self._cookies.load(header)
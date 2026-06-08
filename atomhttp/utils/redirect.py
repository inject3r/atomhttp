"""
Redirect Handler Module
-----------------------
Handles HTTP redirect responses for the AtomHTTP client.

This module provides the RedirectHandler class which manages redirect
following logic, including checking redirect status codes, tracking
redirect counts, and constructing absolute URLs from relative redirect
locations.
"""

from typing import Optional
from urllib.parse import urlparse, urlunparse


class RedirectHandler:
    """
    Handle HTTP redirect responses and manage redirect limits.
    
    This class tracks the number of redirects followed and provides
    utilities for determining when to follow redirects and how to
    construct absolute redirect URLs from relative locations.
    
    The handler supports standard HTTP redirect status codes:
        - 301: Moved Permanently
        - 302: Found (Temporary Redirect)
        - 303: See Other
        - 307: Temporary Redirect
        - 308: Permanent Redirect
    
    Attributes:
        max_redirects (int): Maximum number of redirects to follow
        redirect_count (int): Current count of redirects followed
    """
    
    def __init__(self, max_redirects: int = 5):
        """
        Initialize redirect handler with maximum redirect limit.
        
        Args:
            max_redirects (int): Maximum number of redirects to follow.
                                Defaults to 5, which is the standard for
                                most HTTP clients.
        """
        self.max_redirects = max_redirects
        self.redirect_count = 0
    
    def should_redirect(self, status_code: int) -> bool:
        """
        Determine if a status code indicates a redirect response.
        
        This method checks if the HTTP status code is one of the standard
        redirect codes that should be followed automatically.
        
        Args:
            status_code (int): HTTP status code from response
            
        Returns:
            bool: True if status code is a redirect (301, 302, 303, 307, 308),
                  False otherwise
        """
        return status_code in (301, 302, 303, 307, 308)
    
    def is_max_reached(self) -> bool:
        """
        Check if the maximum number of redirects has been reached.
        
        Returns:
            bool: True if redirect_count >= max_redirects, False otherwise
        
        Note:
            When this returns True, the client should stop following
            redirects to avoid infinite loops.
        """
        return self.redirect_count >= self.max_redirects
    
    def get_redirect_url(self, location: str, original_url: str) -> str:
        """
        Convert a redirect location header to an absolute URL.
        
        The Location header in HTTP redirects may be either absolute
        (complete URL) or relative (path only). This method resolves
        relative locations to absolute URLs using the original request URL.
        
        Args:
            location (str): The Location header value from redirect response
            original_url (str): The original URL that was requested
        
        Returns:
            str: Absolute URL to redirect to
        """
        # If location is already absolute, return it directly
        if location.startswith(('http://', 'https://')):
            return location
        
        # Parse the original URL to extract scheme and host
        parsed = urlparse(original_url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        
        # Handle absolute path (starts with '/')
        if location.startswith('/'):
            return base + location
        
        # Handle relative path (no leading '/')
        # Remove the last segment from the original path to get directory
        path = parsed.path.rsplit('/', 1)[0]
        return base + path + '/' + location
"""
Basic Authentication Module
---------------------------
This module provides Basic HTTP Authentication support for the AtomHTTP client.

Basic Authentication is a simple authentication scheme built into the HTTP
protocol. The client sends the username and password encoded in base64 within
the Authorization header.
"""

import base64
from typing import Dict


class BasicAuth:
    """
    Basic Authentication handler for HTTP requests.
    
    This class implements the HTTP Basic Authentication scheme as defined in
    RFC 7617. It handles the encoding of username and password credentials
    into the standard Basic authentication header format.
    
    How Basic Auth Works:
        1. Credentials are combined as "username:password"
        2. The combined string is encoded using Base64
        3. The encoded string is prefixed with "Basic " and sent in the
           Authorization header
        
    Security Considerations:
        - Base64 encoding is NOT encryption; it's easily reversible
        - Basic Auth should ONLY be used over HTTPS connections
        - Credentials are sent with every request
        
    Attributes:
        username (str): The authentication username
        password (str): The authentication password
    
    Example:
        >>> auth = BasicAuth('admin', 'secret123')
        >>> headers = auth.get_header()
        >>> response = await client.get('/protected', headers=headers)
    """
    
    def __init__(self, username: str, password: str):
        """
        Initialize Basic Authentication with username and password.
        
        Args:
            username (str): The username for authentication
            password (str): The password for authentication
        
        Note:
            Username and password are stored in plain text in memory.
            Always use HTTPS when using Basic Authentication.
        """
        self.username = username
        self.password = password
    
    def get_header(self) -> Dict[str, str]:
        """
        Generate the HTTP Authorization header for Basic Authentication.
        
        This method encodes the username and password credentials according
        to the Basic Authentication scheme and returns a dictionary ready
        to be merged into request headers.
        
        The encoding process:
            1. Combine username and password with a colon: "user:pass"
            2. Encode the result to bytes using UTF-8
            3. Apply Base64 encoding to the bytes
            4. Decode back to string and prefix with "Basic "
        
        Returns:
            Dict[str, str]: A dictionary containing the Authorization header.
                           Format: {'Authorization': 'Basic <base64-credentials>'}
        
        Example:
            >>> auth = BasicAuth('john', 'secret')
            >>> header = auth.get_header()
            >>> print(header)
            {'Authorization': 'Basic am9objpzZWNyZXQ='}
        """
        # Combine username and password with colon separator as per RFC 7617
        credentials = f"{self.username}:{self.password}"
        
        # Encode to bytes, then apply Base64 encoding
        encoded = base64.b64encode(credentials.encode()).decode()
        
        # Return the complete Authorization header
        return {'Authorization': f'Basic {encoded}'}
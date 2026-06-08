"""
Bearer Token Authentication Module
----------------------------------
This module provides Bearer Token authentication support for the AtomHTTP client.

Bearer Token authentication (also known as Token-based authentication) is widely
used in RESTful APIs, particularly with OAuth 2.0. The client sends a token
in the Authorization header to prove identity.
"""

from typing import Dict


class BearerAuth:
    """
    Bearer Token authentication handler for HTTP requests.
    
    This class implements the Bearer Token authentication scheme as defined in
    RFC 6750. It adds an Authorization header with the Bearer token to HTTP
    requests, which is the standard way to authenticate with OAuth 2.0 and
    many modern REST APIs.
    
    How Bearer Auth Works:
        1. Client obtains a token (JWT, opaque string, etc.) from an auth server
        2. Token is sent in the Authorization header as "Bearer <token>"
        3. Server validates the token and grants access if valid
    
    Security Considerations:
        - Tokens should be kept secure and never exposed in logs or URLs
        - Tokens typically have expiration times for security
        - Always use HTTPS to prevent token interception
        - Consider implementing token refresh mechanisms
    
    Attributes:
        token (str): The bearer token string used for authentication
    
    Example:
        >>> auth = BearerAuth('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...')
        >>> headers = auth.get_header()
        >>> response = await client.get('/api/protected', headers=headers)
    """
    
    def __init__(self, token: str):
        """
        Initialize Bearer Token authentication with a token string.
        
        Args:
            token (str): The bearer token string. This is typically a JWT
                        (JSON Web Token) or an opaque string provided by
                        the authentication server.
        
        Note:
            The token is stored in plain text in memory. Ensure proper
            handling and cleanup of tokens when no longer needed.
        
        Example:
            >>> auth = BearerAuth('your-api-token-here')
        """
        self.token = token
    
    def get_header(self) -> Dict[str, str]:
        """
        Generate the HTTP Authorization header for Bearer Token authentication.
        
        This method creates the standard Authorization header format required
        by RFC 6750 for Bearer token authentication. The token is prefixed
        with "Bearer " to indicate the authentication scheme.
        
        The resulting header format:
            Authorization: Bearer <token>
        
        Returns:
            Dict[str, str]: A dictionary containing the Authorization header.
                           Format: {'Authorization': 'Bearer <token>'}
        
        Example:
            >>> auth = BearerAuth('abc123xyz')
            >>> header = auth.get_header()
            >>> print(header)
            {'Authorization': 'Bearer abc123xyz'}
        """
        # Return the Authorization header with Bearer scheme prefix
        return {'Authorization': f'Bearer {self.token}'}
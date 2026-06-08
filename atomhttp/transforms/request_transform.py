"""
Request Transformer Module
--------------------------
Handles transformation of request data before sending.

This module provides the RequestTransformer class which applies various
transformations to request configurations before they are sent over the
network. Transformations include custom transform functions, automatic
Content-Type header setting, and Basic authentication header generation.
"""

import json
import base64
from typing import Any
from ..core.config import RequestConfig


class RequestTransformer:
    """
    Transform request data before it is sent over the network.
    
    This class applies a series of transformations to RequestConfig objects
    to prepare them for HTTP transmission. Transformations are applied in
    a specific order:
        1. Custom transformRequest function (if provided by user)
        2. Automatic Content-Type header detection and setting
        3. Basic authentication header generation (if auth credentials provided)
    
    The transformer is idempotent and can be called multiple times without
    adverse effects, though it's designed to be called once per request.
    """
    
    def transform(self, config: RequestConfig) -> RequestConfig:
        """
        Apply all request transformations to the configuration.
        
        This method modifies the request configuration in place and returns
        it for method chaining. Transformations are applied in sequence:
        
        1. Custom transformation: If config.transformRequest is provided,
           it is called with the current data and the result becomes the
           new data.
        
        2. Content-Type auto-detection: If data is present and no
           Content-Type header is set, the header is automatically added
           based on data type (dict -> JSON, str -> text/plain).
        
        3. Basic Authentication: If config.auth contains username and
           password, an Authorization header with Basic scheme is added.
        
        Args:
            config (RequestConfig): The request configuration to transform
            
        Returns:
            RequestConfig: The same configuration object after transformations
                          (modified in place for efficiency)
        
        Example:
            >>> transformer = RequestTransformer()
            >>> config = RequestConfig(
            ...     data={'name': 'John'},
            ...     auth={'username': 'user', 'password': 'pass'}
            ... )
            >>> transformed = transformer.transform(config)
            >>> print(transformed.headers['Content-Type'])
            'application/json'
            >>> print(transformed.headers['Authorization'])
            'Basic dXNlcjpwYXNz'
        """
        # Apply custom request transformation if provided by user
        # This allows users to modify data before any auto-transformations
        if config.transformRequest:
            config.data = config.transformRequest(config.data)
        
        # Automatically set Content-Type header based on data type
        # Only applies if data exists and no Content-Type is already set
        if config.data and 'Content-Type' not in config.headers:
            if isinstance(config.data, dict):
                # Dictionary data -> JSON format
                config.headers['Content-Type'] = 'application/json'
                config.data = json.dumps(config.data)
            elif isinstance(config.data, str):
                # String data -> plain text
                config.headers['Content-Type'] = 'text/plain'
        
        # Handle Basic Authentication
        # If auth dictionary contains username and password, generate Basic auth header
        if config.auth:
            # Combine username and password with colon separator
            auth_str = f"{config.auth.get('username', '')}:{config.auth.get('password', '')}"
            # Base64 encode the credentials
            encoded = base64.b64encode(auth_str.encode()).decode()
            # Add the Authorization header
            config.headers['Authorization'] = f"Basic {encoded}"
        
        return config
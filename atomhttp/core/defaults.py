"""
Defaults Configuration Module
-----------------------------
Manages default configuration settings for the AtomHTTP client.

This module provides the Defaults class which maintains the default
configuration values for all AtomHTTP client instances. It supports
merging custom configurations with defaults, updating individual
settings, and accessing default values as attributes.
"""

from typing import Dict, Any
from .config import RequestConfig


class Defaults:
    """
    Default configuration manager for AtomHTTP client instances.
    
    This class holds the default configuration that will be applied to
    all requests made by a AtomHTTP client unless overridden. It supports
    updating defaults with custom values, accessing defaults as attributes,
    and converting defaults to dictionary format.
    
    The Defaults class is designed to be used internally by the AtomHTTP
    client, but can also be accessed directly for advanced use cases.
    
    Features:
        - Centralized default configuration management
        - Deep merging of header dictionaries
        - Attribute-style access to configuration values
        - Support for updating individual settings
        - Dictionary conversion for serialization
    
    Attributes:
        _config (RequestConfig): Internal RequestConfig object holding all
                                default values.
    
    Example:
        >>> defaults = Defaults()
        >>> print(defaults.timeout)
        30
        >>> defaults.timeout = 60
        >>> print(defaults.timeout)
        60
        >>> defaults.update(RequestConfig(headers={'X-Custom': 'value'}))
        >>> print(defaults.headers['X-Custom'])
        'value'
    """
    
    def __init__(self):
        """
        Initialize default configuration with sensible defaults.
        
        Default values are chosen to provide a balanced experience
        between security, performance, and compatibility:
            - Accept header accepts JSON, text, and any format
            - User-Agent identifies the client as atomhttp/2.0.0
            - 30 second timeout prevents hanging requests
            - Up to 5 redirects followed automatically
            - JSON response parsing by default
            - CSRF protection enabled with standard header names
            - Credentials not sent cross-origin by default
            - Keep-alive enabled for connection reuse
            - Automatic gzip/deflate decompression enabled
        """
        self._config = RequestConfig(
            # Default headers for all requests
            headers={
                'Accept': 'application/json, text/plain, */*',
                'User-Agent': 'atomhttp/2.0.0'
            },
            # Request timeout in seconds
            timeout=30,
            # Maximum number of redirects to follow
            maxRedirects=5,
            # Default response parsing type
            responseType='json',
            # CSRF protection cookie name
            xsrfCookieName='XSRF-TOKEN',
            # CSRF protection header name
            xsrfHeaderName='X-XSRF-TOKEN',
            # Do not send credentials cross-origin by default
            withCredentials=False,
            # Enable HTTP keep-alive for connection reuse
            keepAlive=True,
            # Automatically decompress compressed responses
            decompress=True,
            # No base URL by default (use absolute URLs)
            baseURL=''
        )
    
    def update(self, config: RequestConfig):
        """
        Update default configuration with values from another config.
        
        This method merges the provided configuration into the defaults.
        Headers are merged (custom headers added, existing ones overwritten),
        while other fields are replaced entirely if non-None.
        
        Args:
            config (RequestConfig): Configuration containing values to merge
                                   into the defaults. Only non-None values
                                   are considered for the update.
        
        Example:
            >>> defaults = Defaults()
            >>> custom = RequestConfig(
            ...     headers={'X-API-Key': '12345'},
            ...     timeout=15
            ... )
            >>> defaults.update(custom)
            >>> print(defaults.timeout)  # Updated to 15
            >>> print(defaults.headers['X-API-Key'])  # New header added
        """
        # Convert config to dictionary for iteration
        config_dict = config.to_dict()
        
        # Process each key-value pair
        for key, value in config_dict.items():
            # Skip None values (they represent no change)
            if value is not None and hasattr(self._config, key):
                # Special handling for headers: merge dictionaries instead of replacing
                if key == 'headers' and isinstance(value, dict):
                    self._config.headers.update(value)
                else:
                    # Replace other attributes directly
                    setattr(self._config, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert all default configuration to a dictionary.
        
        This method returns a complete dictionary representation of the
        current default configuration, with None values omitted.
        
        Returns:
            Dict[str, Any]: Dictionary containing all non-None default
                           configuration values.
        
        Example:
            >>> defaults = Defaults()
            >>> defaults_dict = defaults.to_dict()
            >>> print(defaults_dict.keys())
            dict_keys(['headers', 'timeout', 'maxRedirects', ...])
        """
        return self._config.to_dict()
    
    def __getattr__(self, name):
        """
        Access configuration values as attributes.
        
        This magic method allows direct attribute access to configuration
        values stored in the internal _config object.
        
        Args:
            name (str): Name of the configuration attribute to retrieve
            
        Returns:
            Any: Value of the requested configuration attribute
            
        Raises:
            AttributeError: If the attribute doesn't exist in _config
        
        Example:
            >>> defaults = Defaults()
            >>> print(defaults.timeout)  # Access via __getattr__
            30
        """
        return getattr(self._config, name)
    
    def __setattr__(self, name, value):
        """
        Set configuration values as attributes.
        
        This magic method routes attribute assignment to the internal
        _config object, except for the special '_config' attribute itself.
        
        Args:
            name (str): Name of the configuration attribute to set
            value (Any): Value to assign to the configuration attribute
        
        Example:
            >>> defaults = Defaults()
            >>> defaults.timeout = 45  # Sets _config.timeout = 45
        """
        # Special handling for the internal _config attribute
        if name == '_config':
            super().__setattr__(name, value)
        else:
            # Route all other attribute assignments to the _config object
            setattr(self._config, name, value)
    
    @property
    def baseURL(self) -> str:
        """
        Get the base URL configured in defaults.
        
        Returns:
            str: Current base URL value (empty string if not set)
        """
        return self._config.baseURL
    
    @baseURL.setter
    def baseURL(self, value: str):
        """
        Set the base URL in defaults.
        
        Args:
            value (str): New base URL value to set
        """
        self._config.baseURL = value
"""
Request Handler Module
----------------------
Core request execution engine for AtomHTTP client.

This module contains the RequestHandler class which orchestrates the entire
request lifecycle including interceptor execution, request transformation,
adapter selection, response transformation, and comprehensive error handling.
"""

import asyncio
import aiohttp
from typing import Optional, Any
from .config import RequestConfig
from .response import Response
from .adapters import HTTPAdapter
from ..transforms.request_transform import RequestTransformer
from ..transforms.response_transform import ResponseTransformer
from ..errors.http_errors import (
    AtomHTTPRequestError, 
    AtomHTTPTimeoutError, 
    AtomHTTPNetworkError,
    AtomHTTPError
)


class RequestHandler:
    """
    Core request handler that orchestrates the entire HTTP request lifecycle.
    
    This class is responsible for executing HTTP requests through a pipeline
    of interceptors, transformers, and adapters. It manages the flow of
    request execution from start to finish, applying all configured
    middleware and transformations.
    
    The request flow follows this sequence:
        1. Request interceptors are applied (can modify config)
        2. Request data transformation is applied
        3. URL validation is performed
        4. HTTP adapter is selected and request is sent
        5. Response transformation is applied
        6. Response interceptors are applied
        
    Attributes:
        defaults: Default configuration object for the client
        interceptors (InterceptorManager): Manager for request/response interceptors
        request_transformer (RequestTransformer): Handles request data transformation
        response_transformer (ResponseTransformer): Handles response data transformation
        default_adapter (HTTPAdapter): Default HTTP adapter for network requests
    """
    
    def __init__(self, defaults, interceptor_manager):
        """
        Initialize the request handler with defaults and interceptors.
        
        Args:
            defaults: Default configuration object containing base settings
            interceptor_manager: Manager instance holding registered interceptors
        """
        self.defaults = defaults
        self.interceptors = interceptor_manager
        self.request_transformer = RequestTransformer()
        self.response_transformer = ResponseTransformer()
        self.default_adapter = HTTPAdapter()
    
    async def execute(self, config: RequestConfig) -> Response:
        """
        Execute a complete HTTP request through the full processing pipeline.
        
        This method orchestrates the entire request execution process:
            1. Apply request interceptors (modify config before request)
            2. Transform request data (serialization, auth headers, etc.)
            3. Validate URL format
            4. Select and execute HTTP adapter (network request)
            5. Transform response data
            6. Apply response interceptors (modify response after request)
        
        Args:
            config (RequestConfig): Complete request configuration
            
        Returns:
            Response: Final response after all transformations and interceptors
            
        Raises:
            AtomHTTPRequestError: Invalid request or URL
            AtomHTTPTimeoutError: Request timeout exceeded
            AtomHTTPNetworkError: Network connectivity issues
            AtomHTTPError: Base exception for all AtomHTTP errors
        """
        try:
            # Step 1: Apply all registered request interceptors
            # These can modify headers, add auth, log requests, etc.
            modified_config = await self._apply_request_interceptors(config)
            
            # Step 2: Transform request data (JSON serialization, auth headers, etc.)
            transformed_config = self.request_transformer.transform(modified_config)
            
            # Step 3: Validate that URL exists and has proper protocol
            if not transformed_config.url:
                raise AtomHTTPRequestError(
                    "URL is required",
                    request=transformed_config,
                    config=transformed_config
                )
            
            # Ensure URL uses HTTP or HTTPS protocol
            if not (transformed_config.url.startswith('http://') or transformed_config.url.startswith('https://')):
                raise AtomHTTPRequestError(
                    f"Invalid URL: {transformed_config.url}. URL must start with http:// or https://",
                    request=transformed_config,
                    config=transformed_config
                )
            
            # Step 4: Select adapter (custom or default) and execute request
            adapter = transformed_config.adapter or self.default_adapter
            response = await adapter.send(transformed_config)
            
            # Step 5: Transform response data (parse JSON, modify structure, etc.)
            transformed_response = self.response_transformer.transform(response)
            
            # Step 6: Apply all registered response interceptors
            final_response = await self._apply_response_interceptors(transformed_response)
            
            return final_response
            
        # Re-raise AtomHTTP errors without modification
        except AtomHTTPError:
            raise
        
        # Convert asyncio timeout to AtomHTTP timeout error
        except asyncio.TimeoutError:
            error = AtomHTTPTimeoutError(
                f"Request timeout after {config.timeout}s",
                config=config,
                request=config
            )
            error.code = 'ECONNABORTED'
            raise error
        
        # Convert aiohttp client errors to AtomHTTP network errors
        except aiohttp.ClientError as e:
            error = AtomHTTPNetworkError(str(e), config=config)
            error.code = 'ERR_NETWORK'
            raise error
        
        # Convert any other exception to AtomHTTP request error
        except Exception as e:
            if not isinstance(e, AtomHTTPError):
                error = AtomHTTPRequestError(str(e), request=config, config=config)
                error.code = 'ERR_BAD_REQUEST'
                raise error
            raise
    
    async def _apply_request_interceptors(self, config: RequestConfig) -> RequestConfig:
        """
        Apply all registered request interceptors in sequence.
        
        Request interceptors are executed in the order they were registered.
        Each interceptor receives the current configuration and returns a
        (potentially modified) configuration for the next interceptor.
        
        Args:
            config (RequestConfig): Current request configuration
            
        Returns:
            RequestConfig: Configuration after all interceptors have been applied
            
        Raises:
            AtomHTTPRequestError: If any interceptor fails or returns invalid type
        """
        for idx, interceptor in enumerate(self.interceptors.request_interceptors):
            try:
                # Execute interceptor (supports both sync and async functions)
                result = interceptor(config)
                if asyncio.iscoroutine(result):
                    config = await result
                else:
                    config = result
                
                # Validate interceptor return type
                if not isinstance(config, RequestConfig):
                    raise AtomHTTPRequestError(
                        f"Request interceptor {idx} must return RequestConfig",
                        request=config,
                        config=config
                    )
            except AtomHTTPError:
                raise
            except Exception as e:
                # Wrap any interceptor exception in AtomHTTP error
                raise AtomHTTPRequestError(
                    f"Request interceptor {idx} error: {str(e)}",
                    request=config,
                    config=config
                )
        return config
    
    async def _apply_response_interceptors(self, response: Response) -> Response:
        """
        Apply all registered response interceptors in sequence.
        
        Response interceptors are executed in the order they were registered.
        Each interceptor receives the current response and returns a
        (potentially modified) response for the next interceptor.
        
        Args:
            response (Response): Current response object
            
        Returns:
            Response: Response after all interceptors have been applied
            
        Raises:
            AtomHTTPRequestError: If any interceptor fails or returns invalid type
        """
        for idx, interceptor in enumerate(self.interceptors.response_interceptors):
            try:
                # Execute interceptor (supports both sync and async functions)
                result = interceptor(response)
                if asyncio.iscoroutine(result):
                    response = await result
                else:
                    response = result
                
                # Validate interceptor return type
                if not isinstance(response, Response):
                    raise AtomHTTPRequestError(
                        f"Response interceptor {idx} must return Response",
                        request=response.config,
                        config=response.config
                    )
            except AtomHTTPError:
                raise
            except Exception as e:
                # Wrap any interceptor exception in AtomHTTP error
                raise AtomHTTPRequestError(
                    f"Response interceptor {idx} error: {str(e)}",
                    request=response.config,
                    config=response.config
                )
        return response
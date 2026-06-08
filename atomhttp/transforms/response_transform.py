"""
Response Transformer Module
---------------------------
Handles transformation of response data after receiving.

This module provides the ResponseTransformer class which applies transformations
to response data before it is returned to the caller. Transformations include
custom transformResponse functions provided by the user.
"""

import json
from ..core.response import Response


class ResponseTransformer:
    """
    Transform response data after it is received from the network.
    
    This class applies user-defined transformations to response data before
    the response object is returned to the caller. The primary use case is
    the transformResponse function that users can configure to modify or
    preprocess response data.
    
    Transformations are applied in order:
        1. Custom transformResponse function (if provided by user)
    
    The transformer is idempotent and can be called multiple times without
    adverse effects, though it's designed to be called once per response.
    """
    
    def transform(self, response: Response) -> Response:
        """
        Apply all response transformations to the response object.
        
        This method modifies the response data in place and returns the
        response object for method chaining. The primary transformation is:
        
        1. Custom transformation: If response.config.transformResponse is
           provided, it is called with the current response data and the
           result becomes the new response data.
        
        This allows users to implement features like:
            - Automatic date parsing
            - Data normalization
            - Error structure standardization
            - Response caching
            - Logging or analytics
        
        Args:
            response (Response): The response object to transform
            
        Returns:
            Response: The same response object after transformations
                     (modified in place for efficiency)
        
        Example:
            >>> transformer = ResponseTransformer()
            >>> config = RequestConfig(transformResponse=lambda data: data.get('result', {}))
            >>> response = Response(
            ...     data={'result': {'id': 1, 'name': 'John'}},
            ...     config=config,
            ...     ...
            ... )
            >>> transformed = transformer.transform(response)
            >>> print(transformed.data)
            {'id': 1, 'name': 'John'}
        """
        # Apply custom response transformation if provided by user
        # This allows users to modify or extract data before it reaches their code
        if response.config.transformResponse:
            response.data = response.config.transformResponse(response.data)
        
        return response
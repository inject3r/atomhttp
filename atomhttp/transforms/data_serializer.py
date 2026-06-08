"""
Data Serializer Module
----------------------
Provides data serialization and deserialization utilities for different formats.

This module contains the DataSerializer class with static methods for converting
between Python data structures and various wire formats used in HTTP requests
and responses, including JSON and URL-encoded form data.
"""

import json
from typing import Any


class DataSerializer:
    """
    Serialize and deserialize data for different content types.
    
    This utility class provides static methods for common data format
    conversions needed in HTTP communication. It handles JSON serialization
    and parsing, as well as URL-encoded form data serialization.
    
    All methods are static, so the class is not meant to be instantiated.
    """
    
    @staticmethod
    def serialize_json(data: Any) -> str:
        """
        Serialize Python object to JSON string.
        
        Converts Python data structures (dict, list, str, int, float, bool, None)
        to a JSON formatted string. This is the inverse of to_json().
        
        Args:
            data (Any): Python object to serialize. Must be JSON-serializable.
                       Common types: dict, list, str, int, float, bool, None
        
        Returns:
            str: JSON string representation of the input data
        
        Raises:
            TypeError: If data contains non-serializable types
            ValueError: If circular references are detected
        
        Example:
            >>> DataSerializer.serialize_json({'name': 'John', 'age': 30})
            '{"name": "John", "age": 30}'
        """
        return json.dumps(data)
    
    @staticmethod
    def serialize_form_data(data: dict) -> str:
        """
        Serialize dictionary to URL-encoded form data string.
        
        Converts a dictionary of key-value pairs into a URL-encoded string
        suitable for use as application/x-www-form-urlencoded body.
        Values are automatically percent-encoded.
        
        Args:
            data (dict): Dictionary of form fields. Keys and values are
                        converted to strings and URL-encoded.
        
        Returns:
            str: URL-encoded string in format 'key1=value1&key2=value2'
        
        Example:
            >>> DataSerializer.serialize_form_data({'name': 'John Doe', 'age': 30})
            'name=John%20Doe&age=30'
        """
        from urllib.parse import urlencode
        return urlencode(data)
    
    @staticmethod
    def to_json(data: str) -> Any:
        """
        Parse JSON string to Python object.
        
        Deserializes a JSON formatted string back into a Python data structure.
        This is the inverse of serialize_json().
        
        Args:
            data (str): JSON string to parse
        
        Returns:
            Any: Python object (dict, list, str, int, float, bool, None)
                depending on the JSON content
        
        Raises:
            json.JSONDecodeError: If the string is not valid JSON
        
        Example:
            >>> DataSerializer.to_json('{"name": "John", "age": 30}')
            {'name': 'John', 'age': 30}
        """
        return json.loads(data)
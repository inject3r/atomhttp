"""
FormData Module
---------------
Provides multipart/form-data and URL-encoded form data handling for AtomHTTP.

This module implements a FormData class that mimics the browser's FormData API,
allowing easy construction of form data for HTTP requests. It supports:
    - Multiple values for the same field name
    - File uploads with automatic MIME type detection
    - Mixed field and file data in the same form
    - Streaming of file contents without loading entire files into memory
    - Conversion to both multipart/form-data and application/x-www-form-urlencoded formats
"""

import io
import os
import random
import string
from typing import Dict, Any, Optional, Union, Tuple, List
from pathlib import Path
from urllib.parse import urlencode


class FormDataItem:
    """
    Represents a single item in a FormData field.
    
    FormData fields can have multiple values (e.g., for multi-select inputs),
    and each value is stored as a FormDataItem. This class holds the value
    along with optional metadata for file uploads.
    
    Attributes:
        value (Any): The actual data value (string, bytes, file-like, Path, etc.)
        filename (Optional[str]): Original filename for file uploads
        content_type (Optional[str]): MIME type of the file content
    """
    
    def __init__(self, value: Any, filename: Optional[str] = None, content_type: Optional[str] = None):
        """
        Initialize a form data item.
        
        Args:
            value (Any): The data value. Can be string, bytes, file object, Path, etc.
            filename (Optional[str]): Original filename (for file uploads)
            content_type (Optional[str]): MIME type (auto-detected if not provided)
        """
        self.value = value
        self.filename = filename
        self.content_type = content_type


class FormData:
    """
    FormData implementation similar to browser FormData API.
    
    This class provides a convenient interface for constructing form data
    suitable for HTTP requests, supporting both multipart/form-data (for
    file uploads and mixed content) and URL-encoded (for simple forms).
    
    Features:
        - Append multiple values to the same field name
        - Automatic MIME type detection from file extensions
        - Support for various value types (str, bytes, file objects, Path)
        - Streaming of large file contents
        - Boundary generation for multipart requests
    """
    
    def __init__(self):
        """
        Initialize an empty FormData object.
        
        The internal data structure maps field names to lists of FormDataItem
        objects, allowing multiple values per field.
        """
        self._data: Dict[str, List[FormDataItem]] = {}
        self._boundary: Optional[str] = None
    
    def append(self, name: str, value: Any, filename: Optional[str] = None, content_type: Optional[str] = None):
        """
        Append a value to a form data field.
        
        If the field name already exists, the new value is added to the list
        of values for that field (multiple values are allowed).
        
        Args:
            name (str): Field name
            value (Any): Field value (string, bytes, file object, Path, etc.)
            filename (Optional[str]): Original filename (for file uploads)
            content_type (Optional[str]): MIME type (auto-detected from filename if not provided)
        """
        if name not in self._data:
            self._data[name] = []
        
        item = FormDataItem(value, filename, content_type)
        self._data[name].append(item)
    
    def delete(self, name: str):
        """
        Delete all values for a form data field.
        
        Args:
            name (str): Field name to remove
        """
        if name in self._data:
            del self._data[name]
    
    def get(self, name: str) -> Optional[Any]:
        """
        Get the first value of a form data field.
        
        Args:
            name (str): Field name to retrieve
            
        Returns:
            Optional[Any]: First value of the field, or None if field doesn't exist
        """
        if name in self._data and self._data[name]:
            return self._data[name][0].value
        return None
    
    def get_all(self, name: str) -> List[Any]:
        """
        Get all values of a form data field.
        
        Args:
            name (str): Field name to retrieve
            
        Returns:
            List[Any]: List of all values for the field (empty list if field doesn't exist)
        """
        if name in self._data:
            return [item.value for item in self._data[name]]
        return []
    
    def has(self, name: str) -> bool:
        """
        Check if a field exists in the form data.
        
        Args:
            name (str): Field name to check
            
        Returns:
            bool: True if field exists, False otherwise
        """
        return name in self._data
    
    def keys(self) -> List[str]:
        """
        Get all field names in the form data.
        
        Returns:
            List[str]: List of all field names
        """
        return list(self._data.keys())
    
    def values(self) -> List[Any]:
        """
        Get all values in the form data (flattened).
        
        Returns:
            List[Any]: List of all values (all items from all fields)
        """
        return [item.value for items in self._data.values() for item in items]
    
    def items(self) -> List[Tuple[str, Any]]:
        """
        Get all field-value pairs (flattened).
        
        Returns:
            List[Tuple[str, Any]]: List of (field_name, value) tuples
        """
        return [(name, item.value) for name, items in self._data.items() for item in items]
    
    def _generate_boundary(self) -> str:
        """
        Generate a unique multipart boundary string.
        
        The boundary is a random string that separates different parts of
        a multipart/form-data request. It's designed to be unique enough
        to not appear in the actual data.
        
        Returns:
            str: Random boundary string
        """
        return '----WebKitFormBoundary' + ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    
    def to_multipart(self) -> Tuple[bytes, str]:
        """
        Convert form data to multipart/form-data format.
        
        This method serializes the FormData object into the multipart format
        required by HTTP requests. Each field becomes a separate part with
        its own headers and content.
        
        The format follows RFC 7578 (Returning Values from Forms: multipart/form-data).
        
        Returns:
            Tuple[bytes, str]: A tuple containing:
                - bytes: The complete multipart/form-data body
                - str: The boundary string used for the multipart parts
        """
        if not self._boundary:
            self._boundary = self._generate_boundary()
        
        lines = []
        
        for name, items in self._data.items():
            for item in items:
                lines.append(f'--{self._boundary}')
                lines.append(f'Content-Disposition: form-data; name="{name}"')
                
                if item.filename:
                    lines[-1] = f'Content-Disposition: form-data; name="{name}"; filename="{item.filename}"'
                    
                    if item.content_type:
                        lines.append(f'Content-Type: {item.content_type}')
                    else:
                        ext = os.path.splitext(item.filename)[1].lower()
                        content_types = {
                            '.txt': 'text/plain',
                            '.json': 'application/json',
                            '.xml': 'application/xml',
                            '.html': 'text/html',
                            '.css': 'text/css',
                            '.js': 'application/javascript',
                            '.png': 'image/png',
                            '.jpg': 'image/jpeg',
                            '.jpeg': 'image/jpeg',
                            '.gif': 'image/gif',
                            '.pdf': 'application/pdf',
                            '.zip': 'application/zip',
                            '.mp4': 'video/mp4',
                            '.mp3': 'audio/mpeg',
                        }
                        lines.append(f'Content-Type: {content_types.get(ext, "application/octet-stream")}')
                
                lines.append('')
                
                if isinstance(item.value, (bytes, bytearray)):
                    lines.append(item.value)
                elif isinstance(item.value, (io.IOBase, io.BufferedReader)):
                    lines.append(item.value.read())
                elif isinstance(item.value, Path):
                    with open(item.value, 'rb') as f:
                        lines.append(f.read())
                else:
                    lines.append(str(item.value).encode('utf-8'))
                
                lines.append('')
        
        lines.append(f'--{self._boundary}--')
        lines.append('')
        
        result = []
        for line in lines:
            if isinstance(line, bytes):
                result.append(line)
            else:
                result.append(line.encode('utf-8'))
            result.append(b'\r\n')
        
        return b''.join(result), self._boundary
    
    def to_urlencoded(self) -> str:
        """
        Convert form data to application/x-www-form-urlencoded format.
        
        This method serializes the FormData object into the URL-encoded
        format suitable for HTML forms without file uploads.
        
        Note: Only the first value of each field is included in the output.
        Multiple values are not supported in standard URL-encoded forms.
        
        Returns:
            str: URL-encoded form data string
        """
        params = {}
        for name, items in self._data.items():
            if items:
                params[name] = items[0].value
        
        return urlencode(params)
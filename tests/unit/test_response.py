"""
Unit Tests for AtomHTTP Response Module
========================================

This module contains unit tests for the Response class, which represents
HTTP responses in the AtomHTTP client. Tests verify proper initialization,
string representation, and status code validation logic.

The Response class is a core data structure used throughout the library
to encapsulate HTTP response data including body, status code, headers,
and the original request configuration.
"""

import pytest
from atomhttp.core.response import Response


def test_response_creation():
    """
    Test proper initialization of Response objects.
    
    Verifies that all attributes of the Response class are correctly
    set during object creation, including data payload, status code,
    status text, headers, and configuration references.
    """
    response = Response(
        data={'key': 'value'},
        status=200,
        status_text='OK',
        headers={'Content-Type': 'application/json'},
        config=None,
        request=None
    )
    assert response.data == {'key': 'value'}
    assert response.status == 200
    assert response.status_text == 'OK'
    assert response.headers == {'Content-Type': 'application/json'}


def test_response_repr():
    """
    Test the string representation of Response objects.
    
    Verifies that the __repr__ method returns a human-readable string
    containing the HTTP status code and status text, which is useful
    for debugging and logging purposes.
    """
    response = Response(
        data={},
        status=200,
        status_text='OK',
        headers={},
        config=None,
        request=None
    )
    assert 'Response' in repr(response)
    assert '200' in repr(response)


def test_response_ok():
    """
    Test the ok property for status code validation.
    
    Verifies that the ok property returns True for successful status
    codes in the 200-299 range and False for other status codes,
    providing a convenient way to check request success.
    """
    response = Response(
        data={},
        status=200,
        status_text='OK',
        headers={},
        config=None,
        request=None
    )
    assert response.ok is True
    
    response = Response(
        data={},
        status=404,
        status_text='Not Found',
        headers={},
        config=None,
        request=None
    )
    assert response.ok is False
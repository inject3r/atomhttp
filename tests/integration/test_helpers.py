"""
Integration Tests for AtomHTTP Helper Methods
==============================================

This module contains integration tests for helper methods of the
AtomHTTP client, including get_uri() for URL generation and
is_atomhttp_error() for error type identification.

The get_uri() method allows developers to preview the final URL
that will be used for a request without actually executing it,
which is useful for debugging and logging.

The is_atomhttp_error() method provides a reliable way to identify
whether an exception originated from the AtomHTTP library.
"""

import pytest
from atomhttp import AtomHTTP


@pytest.mark.asyncio
async def test_get_uri():
    """
    Test URL generation with baseURL and query parameters.
    
    Verifies that get_uri() correctly combines baseURL, URL path,
    and query parameters into a complete URL string without making
    an actual HTTP request.
    """
    client = AtomHTTP({'baseURL': 'https://api.example.com'})
    uri = client.get_uri({
        'url': '/users',
        'params': {'page': 1, 'limit': 10}
    })
    assert uri == 'https://api.example.com/users?page=1&limit=10'
    await client.close()


@pytest.mark.asyncio
async def test_get_uri_no_base():
    """
    Test URL generation without baseURL configuration.
    
    Verifies that when no baseURL is set, get_uri() uses the absolute
    URL provided and appends query parameters correctly.
    """
    client = AtomHTTP()
    uri = client.get_uri({
        'url': 'https://api.example.com/users',
        'params': {'page': 1}
    })
    assert uri == 'https://api.example.com/users?page=1'
    await client.close()


@pytest.mark.asyncio
async def test_is_atomhttp_error(client):
    """
    Test error type identification for AtomHTTP exceptions.
    
    Verifies that is_atomhttp_error() correctly returns True for
    exceptions raised by the AtomHTTP client (such as network errors)
    and False for standard Python exceptions like ValueError.
    """
    try:
        # This request will fail due to invalid domain name
        await client.get('https://invalid-domain-xyz12345.com', timeout=1)
    except Exception as e:
        assert client.is_atomhttp_error(e) is True
    
    # Verify that non-AtomHTTP exceptions are correctly identified
    assert client.is_atomhttp_error(ValueError('test')) is False
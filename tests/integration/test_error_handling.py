"""
Integration Tests for AtomHTTP Error Handling
==============================================

This module contains integration tests for error handling in the
AtomHTTP client, including timeout errors, network errors, HTTP
status code errors, and error code propagation.

These tests verify that:
    - Timeout errors are correctly raised when requests exceed the timeout limit
    - Network errors are raised for unreachable hosts or DNS failures
    - HTTP error status codes (404) are returned as responses, not exceptions
    - Error objects contain standardized error codes for programmatic handling
    - is_atomhttp_error() correctly identifies library-specific exceptions
"""

import pytest
from atomhttp import AtomHTTP
from atomhttp.errors import AtomHTTPTimeoutError, AtomHTTPNetworkError, AtomHTTPRequestError


@pytest.mark.asyncio
async def test_timeout_error():
    """
    Test that timeout errors are raised when a request exceeds the timeout limit.
    
    Verifies that when a request takes longer than the configured timeout,
    a AtomHTTPTimeoutError is raised. The httpbin.org/delay endpoint
    artificially delays the response, making it perfect for timeout testing.
    """
    client = AtomHTTP({'timeout': 1})
    with pytest.raises(AtomHTTPTimeoutError):
        await client.get('https://httpbin.org/delay/3', timeout=1)
    await client.close()


@pytest.mark.asyncio
async def test_network_error():
    """
    Test that network errors are raised for unreachable hosts.
    
    Verifies that when a request is made to an invalid or unreachable domain,
    a AtomHTTPNetworkError is raised. This covers DNS resolution failures,
    connection refused errors, and general network connectivity issues.
    """
    client = AtomHTTP()
    with pytest.raises(AtomHTTPNetworkError):
        await client.get('https://invalid-domain-xyz12345.com', timeout=2)
    await client.close()


@pytest.mark.asyncio
async def test_404_error(client):
    """
    Test handling of HTTP 404 Not Found status code.
    
    Verifies that HTTP error status codes (4xx, 5xx) are returned as
    normal responses rather than exceptions, allowing developers to
    inspect the status code and handle it appropriately.
    """
    response = await client.get('/status/404')
    assert response.status == 404


@pytest.mark.asyncio
async def test_error_code():
    """
    Test that error objects contain standardized error codes.
    
    Verifies that timeout errors include a 'code' attribute with the
    value 'ECONNABORTED', matching the error code convention used by
    axios and other HTTP clients for easy cross-platform compatibility.
    """
    client = AtomHTTP({'timeout': 1})
    try:
        await client.get('https://httpbin.org/delay/3', timeout=1)
    except AtomHTTPTimeoutError as e:
        assert hasattr(e, 'code')
        assert e.code == 'ECONNABORTED'
    await client.close()


@pytest.mark.asyncio
async def test_is_atomhttp_error(client):
    """
    Test the is_atomhttp_error() helper method.
    
    Verifies that the is_atomhttp_error() method correctly identifies
    exceptions that originate from the AtomHTTP library, distinguishing
    them from standard Python exceptions or exceptions from other libraries.
    """
    try:
        await client.get('https://invalid-domain-xyz12345.com', timeout=1)
    except Exception as e:
        assert client.is_atomhttp_error(e) is True
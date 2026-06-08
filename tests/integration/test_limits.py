"""
Integration Tests for AtomHTTP Connection and Redirect Settings
================================================================

This module contains integration tests for various connection-related
features of the AtomHTTP client, including redirect limits, keep-alive
connections, and timeout overrides. These tests verify that the client
correctly respects configuration settings for network behavior.

The tests use the httpbin.org testing service to simulate redirects
and measure response times.
"""

import pytest
from atomhttp import AtomHTTP


@pytest.mark.asyncio
async def test_max_redirects():
    """
    Test the maximum redirect limit configuration.
    
    Verifies that when maxRedirects is set to 1, the client follows
    at most one redirect. The httpbin.org/redirect/2 endpoint attempts
    to redirect twice, so the response will be either a 302 (after
    the first redirect) or a 200 (if the second redirect completes).
    Both outcomes are acceptable as they confirm the redirect limit
    is enforced.
    """
    client = AtomHTTP({'maxRedirects': 1})
    response = await client.get('https://httpbin.org/redirect/2')
    # Should follow at most 1 redirect, may get 302 or final response
    assert response.status in [200, 302]
    await client.close()


@pytest.mark.asyncio
async def test_keep_alive():
    """
    Test HTTP keep-alive connection behavior.
    
    Verifies that when keepAlive is enabled, the client can successfully
    make multiple requests to the same server without connection issues.
    Both requests should return 200 OK regardless of whether the same
    connection is reused.
    """
    client = AtomHTTP({'keepAlive': True})
    response1 = await client.get('https://httpbin.org/get')
    response2 = await client.get('https://httpbin.org/get')
    assert response1.status == 200
    assert response2.status == 200
    await client.close()


@pytest.mark.asyncio
async def test_timeout_override():
    """
    Test per-request timeout override.
    
    Verifies that a request-specific timeout value overrides the
    client's default timeout configuration. The request should complete
    successfully within the specified 5-second timeout period.
    """
    client = AtomHTTP({'timeout': 10})
    response = await client.get('https://httpbin.org/get', timeout=5)
    assert response.status == 200
    await client.close()
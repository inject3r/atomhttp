"""
Pytest Configuration and Fixtures for AtomHTTP Testing
=======================================================

This module provides pytest fixtures and configuration for the AtomHTTP
test suite. It includes fixtures for creating test clients with different
configurations, sample request/response objects, and event loop management
for asynchronous tests.

Fixtures Provided:
    - client: AtomHTTP client pre-configured with httpbin.org base URL
    - raw_client: AtomHTTP client without any default configuration
    - event_loop: Event loop for async test execution
    - sample_config: Sample RequestConfig object for unit testing
    - sample_response: Sample Response object for unit testing

Usage:
    The fixtures are automatically available to all test files in the
    tests/ directory due to pytest's conftest.py auto-discovery.

Example:
    >>> async def test_get_request(client):
    ...     response = await client.get('/get')
    ...     assert response.status == 200
"""

import pytest
import asyncio
from atomhttp import AtomHTTP
from atomhttp.core.config import RequestConfig
from atomhttp.core.response import Response


@pytest.fixture
async def client():
    """
    Create a test client instance with httpbin.org as base URL.
    
    This client is pre-configured with:
        - baseURL: https://httpbin.org (popular HTTP testing service)
        - timeout: 30 seconds (sufficient for most tests)
        - headers: Accept: application/json (expect JSON responses)
    
    The client is automatically closed after each test to ensure proper
    cleanup of network connections and resources.
    
    Yields:
        AtomHTTP: Configured client instance ready for testing
    
    Example:
        >>> async def test_something(client):
        ...     response = await client.get('/get')
        ...     assert response.status == 200
    """
    client = AtomHTTP({
        'baseURL': 'https://httpbin.org',
        'timeout': 30,
        'headers': {'Accept': 'application/json'}
    })
    yield client
    await client.close()


@pytest.fixture
async def raw_client():
    """
    Create a test client instance without any default configuration.
    
    This client has no base URL and no default headers, making it suitable
    for testing absolute URL requests and verifying that default settings
    don't interfere with test cases.
    
    Yields:
        AtomHTTP: Unconfigured client instance
    
    Example:
        >>> async def test_absolute_url(raw_client):
        ...     response = await raw_client.get('https://httpbin.org/get')
        ...     assert response.status == 200
    """
    client = AtomHTTP()
    yield client
    await client.close()


@pytest.fixture
def event_loop():
    """
    Create and manage an event loop for asynchronous tests.
    
    This fixture provides a dedicated event loop for each test function,
    ensuring proper isolation between tests. The loop is closed after
    each test to prevent event loop resource leaks.
    
    Yields:
        asyncio.AbstractEventLoop: Event loop for async test execution
    
    Note:
        pytest-asyncio typically manages its own event loop, but this
        fixture is provided for cases where explicit loop control is needed.
    """
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_config():
    """
    Create a sample RequestConfig object for unit testing.
    
    This fixture provides a ready-to-use RequestConfig instance with
    realistic values, useful for testing components that work with
    request configurations without making actual network calls.
    
    Returns:
        RequestConfig: Pre-configured request configuration object
    
    Example:
        >>> def test_config_processor(sample_config):
        ...     result = process_config(sample_config)
        ...     assert result.url == 'https://httpbin.org/get'
    """
    return RequestConfig(
        url='https://httpbin.org/get',
        method='GET',
        headers={'X-Test': 'value'},
        timeout=10
    )


@pytest.fixture
def sample_response():
    """
    Create a sample Response object for unit testing.
    
    This fixture provides a ready-to-use Response instance with realistic
    values, useful for testing components that work with response objects
    without requiring actual HTTP requests.
    
    Returns:
        Response: Pre-configured response object with sample data
    
    Example:
        >>> def test_response_processor(sample_response):
        ...     result = process_response(sample_response)
        ...     assert result.data['id'] == 1
    """
    return Response(
        data={'id': 1, 'name': 'test'},
        status=200,
        status_text='OK',
        headers={'Content-Type': 'application/json'},
        config=None,
        request=None
    )
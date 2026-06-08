"""
Unit Tests for AtomHTTP Adapters Module
========================================

This module contains unit tests for the HTTP adapters used by AtomHTTP,
including both the MockAdapter for testing and the HTTPAdapter for
actual network communication.

The MockAdapter tests verify that mock responses can be registered,
sent, and cleared properly. The HTTPAdapter test verifies basic
network connectivity and response handling with the httpbin.org
testing service.
"""

import pytest
from atomhttp.core.adapters import MockAdapter, HTTPAdapter
from atomhttp.core.config import RequestConfig


@pytest.mark.asyncio
async def test_mock_adapter_on():
    """
    Test registration of mock responses.
    
    Verifies that the on() method correctly stores a mock response
    in the adapter's internal dictionary with a key formatted as
    "METHOD:URL".
    """
    mock = MockAdapter()
    mock.on('GET', 'https://api.test/users', {'users': []}, 200)
    assert 'GET:https://api.test/users' in mock._responses


@pytest.mark.asyncio
async def test_mock_adapter_send():
    """
    Test sending a request with a registered mock response.
    
    Verifies that when a request matches a registered mock, the
    adapter returns the predefined response with correct status
    code and data.
    """
    mock = MockAdapter()
    mock.on('GET', 'https://api.test/users', {'users': [{'id': 1}]}, 200)
    
    config = RequestConfig(method='GET', url='https://api.test/users')
    response = await mock.send(config)
    assert response.status == 200
    assert response.data['users'][0]['id'] == 1


@pytest.mark.asyncio
async def test_mock_adapter_not_found():
    """
    Test handling of unmocked requests.
    
    Verifies that when no mock response is registered for a request,
    the adapter returns a 404 Not Found response with an appropriate
    error message.
    """
    mock = MockAdapter()
    config = RequestConfig(method='GET', url='https://api.test/unknown')
    response = await mock.send(config)
    assert response.status == 404
    assert 'No mock found' in str(response.data)


@pytest.mark.asyncio
async def test_mock_adapter_clear():
    """
    Test clearing all registered mock responses.
    
    Verifies that the clear() method removes all previously registered
    mock responses, resetting the adapter to an empty state.
    """
    mock = MockAdapter()
    mock.on('GET', 'https://api.test/users', {'users': []}, 200)
    mock.clear()
    assert len(mock._responses) == 0


@pytest.mark.asyncio
async def test_http_adapter_send():
    """
    Test actual HTTP request using the real HTTPAdapter.
    
    Verifies that the HTTPAdapter can successfully make a network
    request to httpbin.org and receive a valid response. This test
    confirms basic network connectivity and response parsing.
    
    Note: This test makes a real network request and may be affected
    by network conditions or httpbin.org availability.
    """
    adapter = HTTPAdapter()
    config = RequestConfig(method='GET', url='https://httpbin.org/get')
    response = await adapter.send(config)
    assert response.status == 200
    await adapter.close()
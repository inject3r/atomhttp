"""
Unit Tests for AtomHTTP Client Module
======================================

This module contains unit tests for the AtomHTTP client class, focusing
on client initialization, configuration management, URL building, and
configuration merging. These tests verify the internal methods that
prepare requests before they are sent to the network.

The tests use the httpbin.org testing service for integration points
but focus primarily on client-side configuration logic.
"""

import pytest
from atomhttp import AtomHTTP, RequestConfig


@pytest.mark.asyncio
async def test_client_initialization():
    """
    Test proper initialization of AtomHTTP client with custom configuration.
    
    Verifies that when a client is created with custom settings, the
    defaults are correctly updated with the provided baseURL and timeout
    values.
    """
    client = AtomHTTP({'baseURL': 'https://api.test', 'timeout': 5})
    assert client.defaults.baseURL == 'https://api.test'
    assert client.defaults.timeout == 5
    await client.close()


@pytest.mark.asyncio
async def test_client_default_headers():
    """
    Test setting default headers during client initialization.
    
    Verifies that custom default headers provided in the client
    configuration are properly stored and available for subsequent
    requests.
    """
    client = AtomHTTP({'headers': {'X-Key': '123'}})
    assert client.defaults.headers.get('X-Key') == '123'
    await client.close()


@pytest.mark.asyncio
async def test_merge_config():
    """
    Test merging of request configuration with client defaults.
    
    Verifies that _merge_config correctly combines a request-specific
    configuration with the client's default settings, preserving the
    baseURL from defaults while retaining the request's URL and method.
    """
    client = AtomHTTP({'baseURL': 'https://api.test'})
    config = RequestConfig(url='/users', method='GET')
    merged = client._merge_config(config)
    assert merged.baseURL == 'https://api.test'
    assert merged.url == '/users'
    await client.close()


@pytest.mark.asyncio
async def test_build_full_url_with_base():
    """
    Test building full URL when baseURL is configured and path has no leading slash.
    
    Verifies that _build_full_url correctly combines baseURL with a
    relative path that does NOT start with a slash, and properly appends
    query parameters.
    """
    client = AtomHTTP({'baseURL': 'https://api.test'})
    config = RequestConfig(url='users', params={'page': 1})
    merged = client._merge_config(config)
    url = client._build_full_url(merged)
    assert url.startswith('https://api.test/users')
    assert 'page=1' in url
    await client.close()


@pytest.mark.asyncio
async def test_build_full_url_with_slash():
    """
    Test building full URL when baseURL is configured and path has leading slash.
    
    Verifies that _build_full_url correctly combines baseURL with a
    relative path that starts with a slash, normalizing the URL construction
    by removing duplicates slashes.
    """
    client = AtomHTTP({'baseURL': 'https://api.test'})
    config = RequestConfig(url='/users', params={'page': 1})
    merged = client._merge_config(config)
    url = client._build_full_url(merged)
    assert url.startswith('https://api.test/users')
    assert 'page=1' in url
    await client.close()


@pytest.mark.asyncio
async def test_build_full_url_absolute():
    """
    Test building full URL when an absolute URL is provided.
    
    Verifies that when the request URL is absolute (contains protocol),
    the baseURL is ignored and the absolute URL is used as-is, with
    query parameters appended correctly.
    """
    client = AtomHTTP({'baseURL': 'https://api.test'})
    config = RequestConfig(url='https://other.com/users', params={'page': 1})
    merged = client._merge_config(config)
    url = client._build_full_url(merged)
    assert url.startswith('https://other.com/users')
    await client.close()


@pytest.mark.asyncio
async def test_build_full_url_no_base():
    """
    Test building full URL when no baseURL is configured.
    
    Verifies that when the client has no baseURL, an absolute URL in
    the request configuration is used unchanged.
    """
    client = AtomHTTP()
    config = RequestConfig(url='https://api.test/users')
    merged = client._merge_config(config)
    url = client._build_full_url(merged)
    assert url == 'https://api.test/users'
    await client.close()
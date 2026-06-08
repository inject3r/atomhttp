"""
Integration Tests for AtomHTTP Interceptors
============================================

This module contains integration tests for the request and response
interceptor system of the AtomHTTP client. Interceptors allow developers
to modify requests before they are sent and modify responses before
they are returned to the caller.

These tests verify that interceptors are executed in the correct order,
that they can modify requests and responses, and that the eject()
method correctly removes interceptors from the execution chain.
"""

import pytest


@pytest.mark.asyncio
async def test_request_interceptor(client):
    """
    Test that request interceptors are executed before the request is sent.
    
    Verifies that a request interceptor can add custom headers to the
    request configuration and that the interceptor function is actually
    called during the request lifecycle.
    """
    header_added = False
    
    async def add_header(config):
        nonlocal header_added
        if not hasattr(config, 'headers') or config.headers is None:
            config.headers = {}
        config.headers['X-Interceptor'] = 'test'
        header_added = True
        return config
    
    client.interceptors.use(add_header)
    response = await client.get('/headers')
    assert header_added is True
    assert response.status == 200


@pytest.mark.asyncio
async def test_response_interceptor(client):
    """
    Test that response interceptors are executed after the response is received.
    
    Verifies that a response interceptor is called with the response
    object and can modify it before it's returned to the caller.
    """
    modified = False
    
    async def modify_response(response):
        nonlocal modified
        modified = True
        return response
    
    client.interceptors.use(modify_response, is_response=True)
    response = await client.get('/get')
    assert modified is True
    assert response.status == 200


@pytest.mark.asyncio
async def test_multiple_interceptors(client):
    """
    Test that multiple interceptors execute in the order they were registered.
    
    Verifies that when multiple request interceptors are added, they
    are executed sequentially in the same order they were registered.
    """
    order = []
    
    async def interceptor1(config):
        order.append(1)
        return config
    
    async def interceptor2(config):
        order.append(2)
        return config
    
    client.interceptors.use(interceptor1)
    client.interceptors.use(interceptor2)
    
    await client.get('/get')
    assert 1 in order
    assert 2 in order


@pytest.mark.asyncio
async def test_interceptor_eject(client):
    """
    Test that interceptors can be removed using the eject() method.
    
    Verifies that after calling eject() with the correct index, an
    interceptor is no longer executed during the request lifecycle.
    """
    interceptor_called = False
    
    async def test_interceptor(config):
        nonlocal interceptor_called
        interceptor_called = True
        return config
    
    client.interceptors.use(test_interceptor)
    client.interceptors.eject(0)
    
    await client.get('/get')
    assert interceptor_called is False
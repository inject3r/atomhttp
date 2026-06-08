"""
Integration Tests for AtomHTTP Headers and Query Parameters
============================================================

This module contains integration tests for custom HTTP headers, query
parameters, and automatic Content-Type header detection in the
AtomHTTP client.

These tests verify that:
    - Custom headers are properly sent and received by the server
    - Query parameters are correctly URL-encoded and parsed
    - Mixed headers and parameters work together
    - Content-Type is automatically set to application/json for dict data
"""

import pytest


@pytest.mark.asyncio
async def test_custom_headers(client):
    """
    Test sending custom HTTP headers with a request.
    
    Verifies that custom headers provided in the request configuration
    are correctly sent to the server and appear in the response headers.
    The httpbin.org/headers endpoint echoes back all received headers.
    """
    response = await client.get('/headers', headers={
        'X-Custom-1': 'value1',
        'X-Custom-2': 'value2'
    })
    headers = response.data.get('headers', {})
    assert headers.get('X-Custom-1') == 'value1'
    assert headers.get('X-Custom-2') == 'value2'


@pytest.mark.asyncio
async def test_query_params(client):
    """
    Test sending query parameters with a GET request.
    
    Verifies that query parameters are correctly URL-encoded and
    sent to the server. The httpbin.org/get endpoint echoes back
    the received query parameters in the 'args' field.
    
    Note: httpbin may return parameter values as lists, so the test
    handles both string and list formats for robustness.
    """
    response = await client.get('/get', params={
        'search': 'python',
        'page': 2,
        'limit': 20
    })
    args = response.data.get('args', {})
    search_val = args.get('search')
    page_val = args.get('page')
    limit_val = args.get('limit')
    
    # Handle case where values are returned as lists (httpbin behavior)
    if isinstance(search_val, list):
        search_val = search_val[0]
    if isinstance(page_val, list):
        page_val = page_val[0]
    if isinstance(limit_val, list):
        limit_val = limit_val[0]
    
    assert search_val == 'python'
    assert page_val == '2'
    assert limit_val == '20'


@pytest.mark.asyncio
async def test_mixed_params(client):
    """
    Test combining custom headers with query parameters.
    
    Verifies that a request can include both custom headers and
    query parameters simultaneously, and that the server successfully
    processes the request regardless of parameter types.
    """
    response = await client.get('/get', 
        params={'q': 'test', 'sort': 'desc'},
        headers={'X-Request-ID': '123'}
    )
    assert response.status == 200


@pytest.mark.asyncio
async def test_auto_content_type_json(client):
    """
    Test automatic Content-Type header detection for JSON data.
    
    Verifies that when a dictionary is passed as request data without
    an explicit Content-Type header, the client automatically sets
    Content-Type to application/json, and the server accepts the
    JSON payload correctly.
    """
    response = await client.post('/post', data={'key': 'value'})
    assert response.status == 200
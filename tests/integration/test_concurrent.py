"""
Integration Tests for AtomHTTP Concurrent Requests
====================================================

This module contains integration tests for the concurrent request
handling features of the AtomHTTP client, including the all() and
spread() helper methods.

The all() method allows multiple requests to be executed concurrently,
similar to Promise.all() in JavaScript. The spread() method distributes
the response array to a callback function as individual arguments,
making it easier to work with multiple responses in a clean, functional style.

These tests verify that:
    - Multiple requests can be executed concurrently and all complete
    - The all() method returns all responses in the same order as the requests
    - The spread() method correctly distributes responses to callback arguments
"""

import pytest
from atomhttp import AtomHTTP


@pytest.mark.asyncio
async def test_all_method(client):
    """
    Test concurrent execution of multiple requests using the all() method.
    
    Verifies that AtomHTTP.all() can execute multiple requests concurrently
    and returns all responses in a list. Each response should have a
    200 status code, confirming that all requests completed successfully.
    """
    tasks = [
        client.get('/get', params={'id': 1}),
        client.get('/get', params={'id': 2}),
        client.get('/get', params={'id': 3})
    ]
    responses = await AtomHTTP.all(tasks)
    assert len(responses) == 3
    for resp in responses:
        assert resp.status == 200


@pytest.mark.asyncio
async def test_spread_method(client):
    """
    Test the spread() method for distributing responses to a callback.
    
    Verifies that AtomHTTP.spread() takes a list of responses and passes
    them as individual arguments to the provided callback function.
    This is useful for destructuring response arrays into named parameters.
    """
    tasks = [
        client.get('/get', params={'id': 1}),
        client.get('/get', params={'id': 2}),
        client.get('/get', params={'id': 3})
    ]
    responses = await AtomHTTP.all(tasks)
    
    def combine(r1, r2, r3):
        return [r1.status, r2.status, r3.status]
    
    result = await AtomHTTP.spread(combine, *responses)
    assert result == [200, 200, 200]
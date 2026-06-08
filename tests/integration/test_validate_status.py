"""
Integration Tests for AtomHTTP Status Validation
=================================================

This module contains integration tests for the validateStatus feature
of the AtomHTTP client. These tests verify that custom status code
validation functions work correctly, allowing users to define which
HTTP status codes should be considered successful.

The tests use the httpbin.org testing service to simulate various
HTTP status code responses and verify the client's behavior when
custom validation rules are applied.
"""

import pytest
from atomhttp import AtomHTTP
from atomhttp.errors import AtomHTTPRequestError


@pytest.mark.asyncio
async def test_validate_status_200():
    """
    Test status validation that accepts only 200 OK responses.
    
    Verifies that when validateStatus is configured to accept only
    status code 200, a request returning 200 succeeds normally.
    """
    client = AtomHTTP({
        'validateStatus': lambda status: status == 200
    })
    response = await client.get('https://httpbin.org/status/200')
    assert response.status == 200
    await client.close()


@pytest.mark.asyncio
async def test_validate_status_404_fails():
    """
    Test status validation that rejects 404 Not Found responses.
    
    Verifies that when validateStatus is configured to accept only
    status code 200, a request returning 404 raises a AtomHTTPRequestError
    because the status code fails validation.
    """
    client = AtomHTTP({
        'validateStatus': lambda status: status == 200
    })
    with pytest.raises(AtomHTTPRequestError):
        await client.get('https://httpbin.org/status/404')
    await client.close()


@pytest.mark.asyncio
async def test_validate_status_custom_range():
    """
    Test status validation using a custom range (200-299).
    
    Verifies that validateStatus can accept a function that checks
    for a range of status codes (e.g., all 2xx success codes).
    200 passes validation, while 404 fails and raises an exception.
    """
    client = AtomHTTP({
        'validateStatus': lambda status: 200 <= status < 300
    })
    response = await client.get('https://httpbin.org/status/200')
    assert response.status == 200
    
    with pytest.raises(AtomHTTPRequestError):
        await client.get('https://httpbin.org/status/404')
    await client.close()
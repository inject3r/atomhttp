"""
Integration Tests for AtomHTTP Binary Response Types (Blob, ArrayBuffer, Text)
===============================================================================

This module contains integration tests for the various response type
handling capabilities of the AtomHTTP client, including blob (binary),
arraybuffer (binary), and text response types.

These tests verify that:
    - Blob responses correctly return binary data as bytes
    - ArrayBuffer responses return binary data as bytes (alias for blob)
    - Text responses return data as decoded string
    - Image data (PNG) is correctly downloaded and can be validated by its signature
"""

import pytest


@pytest.mark.asyncio
async def test_blob_response(client):
    """
    Test blob response type for binary data download.
    
    Verifies that when response_type='blob' is specified, the response
    data is returned as bytes. The httpbin.org/bytes endpoint generates
    a specific number of random bytes, allowing precise length validation.
    """
    response = await client.get('/bytes/1000', response_type='blob')
    assert isinstance(response.data, bytes)
    assert len(response.data) == 1000


@pytest.mark.asyncio
async def test_arraybuffer_response(client):
    """
    Test arraybuffer response type for binary data download.
    
    Verifies that response_type='arraybuffer' (alias for blob) also
    returns binary data as bytes, matching the behavior of blob responses.
    """
    response = await client.get('/bytes/2000', response_type='arraybuffer')
    assert isinstance(response.data, bytes)
    assert len(response.data) == 2000


@pytest.mark.asyncio
async def test_text_response(client):
    """
    Test text response type for HTML content.
    
    Verifies that when response_type='text' is specified, the response
    data is returned as a decoded string. The httpbin.org/html endpoint
    returns an HTML page, confirming correct text handling.
    """
    response = await client.get('/html', response_type='text')
    assert isinstance(response.data, str)
    assert len(response.data) > 0


@pytest.mark.asyncio
async def test_image_blob(client):
    """
    Test downloading an actual PNG image as blob.
    
    Verifies that image data can be downloaded correctly as a blob
    and validates the PNG file signature (magic bytes) to confirm
    the binary data is intact and properly formatted. The PNG signature
    is 89 50 4E 47 (‰PNG) in hexadecimal.
    """
    response = await client.get('/image/png', response_type='blob')
    assert isinstance(response.data, bytes)
    assert len(response.data) > 100
    # PNG signature (first 8 bytes of a PNG file)
    # The signature is 89 50 4E 47 0D 0A 1A 0A, but first 4 bytes are the unique marker
    assert response.data[:8].hex()[:8] == '89504e47'
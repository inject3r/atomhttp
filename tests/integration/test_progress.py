"""
Integration Tests for AtomHTTP Progress Tracking
=================================================

This module contains integration tests for the upload and download
progress tracking features of the AtomHTTP client. These tests verify
that progress callbacks are correctly invoked during data transfer
operations, providing real-time feedback about transfer status.

The tests use the httpbin.org testing service to simulate data
transfers of known sizes and verify that progress events are fired
with appropriate values.
"""

import pytest


@pytest.mark.asyncio
async def test_download_progress(client):
    """
    Test download progress tracking for binary data.
    
    Verifies that when downloading a 10,000 byte binary file with
    response_type='blob', the on_download_progress callback is invoked
    at least once with progress values, and the complete data is
    correctly received.
    """
    progress_values = []
    
    def on_progress(loaded, total):
        progress_values.append((loaded, total))
    
    response = await client.get(
        '/bytes/10000',
        on_download_progress=on_progress,
        response_type='blob'
    )
    
    # Verify that progress was reported at least once
    assert len(progress_values) > 0
    # Verify successful response
    assert response.status == 200
    # Verify the correct amount of data was downloaded
    assert len(response.data) == 10000


@pytest.mark.asyncio
async def test_upload_progress(client):
    """
    Test upload progress tracking for JSON data.
    
    Verifies that when uploading a 1,000 byte JSON payload, the
    on_upload_progress callback is invoked at least once with
    progress values, and the request completes successfully.
    """
    progress_values = []
    
    def on_progress(loaded, total):
        progress_values.append((loaded, total))
    
    data = {'test': 'x' * 1000}
    response = await client.post(
        '/post',
        data=data,
        on_upload_progress=on_progress
    )
    
    # Verify that progress was reported at least once
    assert len(progress_values) > 0
    # Verify successful response
    assert response.status == 200
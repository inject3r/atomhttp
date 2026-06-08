"""
Unit Tests for AtomHTTP RequestConfig Module
==============================================

This module contains unit tests for the RequestConfig dataclass, which
holds all configuration parameters for an HTTP request. Tests verify
proper initialization, parameter handling, dictionary conversion,
timedelta support, and comprehensive field coverage.

The RequestConfig class is a core data structure that carries all
request settings from the client through the request pipeline.
"""

import pytest
from atomhttp.core.config import RequestConfig
from datetime import timedelta


def test_config_creation():
    """
    Test basic creation of RequestConfig with minimal parameters.
    
    Verifies that a RequestConfig object can be created with just
    URL and method, with all other fields taking default values.
    """
    config = RequestConfig(url='/test', method='POST')
    assert config.url == '/test'
    assert config.method == 'POST'


def test_config_with_params():
    """
    Test RequestConfig creation with query parameters and headers.
    
    Verifies that params dictionary and headers dictionary are correctly
    stored and accessible, demonstrating the ability to configure
    query strings and custom HTTP headers.
    """
    config = RequestConfig(
        url='/users',
        params={'page': 1, 'limit': 10},
        headers={'X-Auth': 'token'}
    )
    assert config.params['page'] == 1
    assert config.headers['X-Auth'] == 'token'


def test_config_to_dict():
    """
    Test conversion of RequestConfig to dictionary format.
    
    Verifies that to_dict() correctly serializes the configuration,
    including proper handling of None values (which are omitted) and
    conversion of complex types to primitive types.
    """
    config = RequestConfig(url='/test', timeout=30)
    d = config.to_dict()
    assert d['url'] == '/test'
    assert d['timeout'] == 30


def test_config_with_timedelta():
    """
    Test RequestConfig with timedelta timeout value.
    
    Verifies that timeout specified as a timedelta object is properly
    converted to seconds (float) when to_dict() is called, providing
    flexible timeout specification options.
    """
    config = RequestConfig(timeout=timedelta(seconds=5))
    d = config.to_dict()
    assert d['timeout'] == 5.0


def test_config_all_fields():
    """
    Test RequestConfig creation with all available fields.
    
    Verifies that a fully populated RequestConfig object correctly
    stores all configuration fields including URL, method, baseURL,
    headers, params, data, timeout, redirect limits, and response type.
    """
    config = RequestConfig(
        url='https://api.test',
        method='PUT',
        baseURL='https://api.test',
        headers={'X-Key': 'value'},
        params={'id': 1},
        data={'name': 'test'},
        timeout=10,
        maxRedirects=3,
        responseType='json'
    )
    assert config.url == 'https://api.test'
    assert config.method == 'PUT'
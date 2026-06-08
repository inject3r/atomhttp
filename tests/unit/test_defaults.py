"""
Unit Tests for AtomHTTP Defaults Module
========================================

This module contains unit tests for the Defaults class, which manages
default configuration settings for AtomHTTP client instances. Tests verify
proper initialization, configuration updates, dictionary conversion,
and attribute access patterns.

The Defaults class provides a centralized way to manage and inherit
default settings across all requests made by a client instance.
"""

import pytest
from atomhttp.core.defaults import Defaults
from atomhttp.core.config import RequestConfig


def test_defaults_initialization():
    """
    Test proper initialization of Defaults object.
    
    Verifies that the default configuration is correctly set during
    object creation, including standard headers like Accept and default
    timeout value of 30 seconds.
    """
    defaults = Defaults()
    assert defaults.headers.get('Accept') == 'application/json, text/plain, */*'
    assert defaults.timeout == 30


def test_defaults_update():
    """
    Test updating default configuration with new values.
    
    Verifies that update() correctly merges a RequestConfig object into
    the existing defaults, overriding existing values and adding new
    headers while preserving unchanged settings.
    """
    defaults = Defaults()
    new_config = RequestConfig(timeout=60, headers={'X-Custom': 'test'})
    defaults.update(new_config)
    assert defaults.timeout == 60
    assert defaults.headers.get('X-Custom') == 'test'


def test_defaults_to_dict():
    """
    Test conversion of defaults to dictionary format.
    
    Verifies that to_dict() returns a complete dictionary representation
    of all default configuration values, containing at minimum the
    timeout and headers keys.
    """
    defaults = Defaults()
    d = defaults.to_dict()
    assert 'timeout' in d
    assert 'headers' in d


def test_defaults_property_access():
    """
    Test attribute-style access to default configuration values.
    
    Verifies that defaults can be accessed and modified using property
    syntax (e.g., defaults.timeout), with changes correctly applied to
    the underlying configuration object.
    """
    defaults = Defaults()
    assert defaults.timeout == 30
    defaults.timeout = 45
    assert defaults.timeout == 45
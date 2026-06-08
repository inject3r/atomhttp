"""
Unit Tests for AtomHTTP Utility Modules
========================================

This module contains unit tests for the utility functions and classes
used throughout the AtomHTTP library, including header merging, URL
building, cookie management, and redirect handling.

These tests focus on isolated functionality without external dependencies,
ensuring that each utility works correctly on its own before being used
in larger components.
"""

import pytest
from atomhttp.utils.helpers import merge_headers, build_url, parse_params
from atomhttp.utils.cookies import CookieManager
from atomhttp.utils.redirect import RedirectHandler


def test_merge_headers():
    """
    Test merging of default and custom headers.
    
    Verifies that:
        - Default headers are preserved when not overridden
        - Custom headers override default headers when keys conflict
        - New headers from custom are added to the result
    """
    default = {'A': '1', 'B': '2'}
    custom = {'B': '3', 'C': '4'}
    merged = merge_headers(default, custom)
    assert merged['A'] == '1'
    assert merged['B'] == '3'
    assert merged['C'] == '4'


def test_build_url():
    """
    Test building complete URLs with base URL, path, and query parameters.
    
    Verifies that:
        - Base URL and path are correctly combined
        - Query parameters are properly URL-encoded
        - Multiple parameters are correctly appended
    """
    url = build_url('https://api.com', '/users', {'page': 1, 'limit': 10})
    assert 'https://api.com/users' in url
    assert 'page=1' in url
    assert 'limit=10' in url


def test_build_url_no_params():
    """
    Test building URLs when no query parameters are provided.
    
    Verifies that the base URL and path are correctly combined without
    adding any query string when params are omitted.
    """
    url = build_url('https://api.com', '/users')
    assert url == 'https://api.com/users'


def test_parse_params():
    """
    Test parsing and filtering of parameter dictionaries.
    
    Verifies that:
        - All values are converted to strings
        - None values are filtered out
        - Valid values are preserved
    """
    params = {'a': 1, 'b': 'test', 'c': None}
    parsed = parse_params(params)
    assert parsed['a'] == '1'
    assert parsed['b'] == 'test'
    assert 'c' not in parsed


def test_cookie_manager_set_get():
    """
    Test setting and retrieving cookies in CookieManager.
    
    Verifies that cookies can be stored and retrieved by name,
    returning the correct value for each cookie.
    """
    cm = CookieManager()
    cm.set_cookie('session', 'abc123')
    assert cm.get_cookie('session') == 'abc123'


def test_cookie_manager_header():
    """
    Test generation of Cookie header string from stored cookies.
    
    Verifies that multiple cookies are correctly formatted into a
    single Cookie header string with proper separator format.
    """
    cm = CookieManager()
    cm.set_cookie('session', 'abc123')
    cm.set_cookie('user', 'john')
    header = cm.get_header()
    assert 'session=abc123' in header
    assert 'user=john' in header


def test_cookie_manager_load_response():
    """
    Test parsing and loading cookies from Set-Cookie response headers.
    
    Verifies that cookies received from server responses are correctly
    parsed and stored, making them available for subsequent requests.
    """
    cm = CookieManager()
    cm.load_from_response('session=xyz789; Path=/')
    assert cm.get_cookie('session') == 'xyz789'


def test_redirect_handler_should_redirect():
    """
    Test detection of HTTP redirect status codes.
    
    Verifies that all standard HTTP redirect status codes (301, 302, 303,
    307, 308) are correctly identified as redirects, while non-redirect
    status codes (like 200) are not.
    """
    handler = RedirectHandler()
    assert handler.should_redirect(301) is True
    assert handler.should_redirect(302) is True
    assert handler.should_redirect(303) is True
    assert handler.should_redirect(307) is True
    assert handler.should_redirect(308) is True
    assert handler.should_redirect(200) is False


def test_redirect_handler_max():
    """
    Test maximum redirect limit tracking.
    
    Verifies that the redirect counter correctly indicates when the
    maximum allowed number of redirects has been reached, preventing
    infinite redirect loops.
    """
    handler = RedirectHandler(max_redirects=3)
    assert handler.is_max_reached() is False
    handler.redirect_count = 3
    assert handler.is_max_reached() is True


def test_redirect_handler_get_url_absolute():
    """
    Test handling of absolute redirect URLs.
    
    Verifies that when the Location header contains an absolute URL
    (with protocol), it is returned unchanged without modification.
    """
    handler = RedirectHandler()
    url = handler.get_redirect_url('https://new.com/path', 'https://old.com')
    assert url == 'https://new.com/path'


def test_redirect_handler_get_url_relative():
    """
    Test resolution of relative redirect URLs to absolute URLs.
    
    Verifies that when the Location header contains a relative path
    (starting with '/'), it is correctly resolved against the original
    request's scheme and host to form an absolute URL.
    """
    handler = RedirectHandler()
    url = handler.get_redirect_url('/new-path', 'https://example.com/old')
    assert url == 'https://example.com/new-path'
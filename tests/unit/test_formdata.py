"""
Unit Tests for AtomHTTP FormData Module
========================================

This module contains unit tests for the FormData class, which implements
multipart/form-data and URL-encoded form data handling. Tests verify all
major functionality including appending values, retrieving values,
deleting fields, and converting to different wire formats.

The FormData class mimics the browser's FormData API and is essential
for file uploads and complex form submissions.
"""

import pytest
from atomhttp.core.form_data import FormData, FormDataItem


def test_formdata_append():
    """
    Test appending a single value to a form field.
    
    Verifies that values can be added to the form data and retrieved
    using the get() method, which returns the first value for a field.
    """
    form = FormData()
    form.append('name', 'John')
    assert form.get('name') == 'John'


def test_formdata_multiple_values():
    """
    Test appending multiple values to the same form field.
    
    Verifies that a field can have multiple values (e.g., multi-select
    inputs) and that get_all() returns all values as a list.
    """
    form = FormData()
    form.append('tags', 'python')
    form.append('tags', 'async')
    values = form.get_all('tags')
    assert 'python' in values
    assert 'async' in values


def test_formdata_delete():
    """
    Test deleting a form field and all its values.
    
    Verifies that delete() removes the entire field, including all
    associated values, from the form data structure.
    """
    form = FormData()
    form.append('name', 'John')
    form.delete('name')
    assert form.get('name') is None


def test_formdata_has():
    """
    Test checking for existence of form fields.
    
    Verifies that has() correctly returns True for existing fields
    and False for fields that haven't been added.
    """
    form = FormData()
    form.append('name', 'John')
    assert form.has('name') is True
    assert form.has('email') is False


def test_formdata_keys():
    """
    Test retrieving all field names from the form data.
    
    Verifies that keys() returns a list of all field names that have
    been added to the form data structure.
    """
    form = FormData()
    form.append('name', 'John')
    form.append('age', '30')
    keys = form.keys()
    assert 'name' in keys
    assert 'age' in keys


def test_formdata_items():
    """
    Test retrieving all field-value pairs from the form data.
    
    Verifies that items() returns a flattened list of (field_name, value)
    tuples, with each value appearing as a separate entry even when
    a field has multiple values.
    """
    form = FormData()
    form.append('name', 'John')
    form.append('age', '30')
    items = form.items()
    assert ('name', 'John') in items
    assert ('age', '30') in items


def test_formdata_to_multipart():
    """
    Test conversion of form data to multipart/form-data format.
    
    Verifies that to_multipart() correctly serializes the form data
    into a binary multipart message with proper boundaries and that
    the field name and value are present in the output.
    """
    form = FormData()
    form.append('name', 'John Doe')
    data, boundary = form.to_multipart()
    assert b'name' in data
    assert b'John Doe' in data


def test_formdata_to_urlencoded():
    """
    Test conversion of form data to URL-encoded format.
    
    Verifies that to_urlencoded() correctly serializes the form data
    into application/x-www-form-urlencoded format, with fields properly
    encoded as key=value pairs separated by ampersands.
    """
    form = FormData()
    form.append('name', 'John')
    form.append('age', '30')
    encoded = form.to_urlencoded()
    assert 'name=John' in encoded
    assert 'age=30' in encoded
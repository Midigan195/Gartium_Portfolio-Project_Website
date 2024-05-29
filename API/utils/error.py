"""
Module: utils/error.py

This module provides functions for generating error responses in Flask applications.
"""

from flask import jsonify

def generate_error_response(form):
    """
    Generates an error response containing form validation errors.

    Args:
        form (FlaskForm): The form object containing validation errors.

    Returns:
        tuple: A tuple containing a JSON response with error details and an HTTP status code (400 for bad request).
    """
    errors = {field: ", ".join(messages) for field, messages in form.errors.items()}
    return jsonify({'error': str(errors)}), 400

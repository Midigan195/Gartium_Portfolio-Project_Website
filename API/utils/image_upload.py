"""
Module: utils/image_upload.py

This module provides functions for validating uploaded images.
"""

import imghdr

def validate_image(file):
    """
    Validates an image file to ensure it is either a JPEG or PNG format.

    Args:
        file (str): The path to the image file to validate.

    Returns:
        bool: True if the image is valid (JPEG or PNG), False otherwise.
    """
    image_type = imghdr.what(file)
    if not image_type or image_type not in ['jpeg', 'png']:
        return False
    return True

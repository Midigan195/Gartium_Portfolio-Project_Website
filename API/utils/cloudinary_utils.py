"""
Module: cloudinary_functions.py

This module provides functions for interacting with the Cloudinary service.
"""

import cloudinary
cloudinary.config(
    cloud_name="dkqmklusp",
    api_key="166526362641378",
    api_secret="6bCzPajL5Eke-dhJLhq9Gs7iAY8",
    api_proxy = "http://proxy.server:3128"
)
from cloudinary.uploader import upload

def upload_image(file):
    """
    Uploads an image file to Cloudinary.

    Args:
        file (str): The path to the image file to upload.

    Returns:
        dict or None: A dictionary containing information about the uploaded image,
                      or None if the upload fails.

    """
    try:
        res = upload(file,
                        transformation=[
                            {'quality': 'auto', 'fetch_format': 'auto', 'max_bytes': 4000000}
                        ],
                )
        return res
    except Exception:
        return None

def delete_image(public_id):
    """
    Deletes an image from Cloudinary.

    Args:
        public_id (str): The public ID of the image to delete.

    Returns:
        bool: True if the image is successfully deleted, False otherwise.

    """
    try:
        cloudinary.uploader.rename(public_id, "purge/" + public_id)
        return True
    except Exception:
        return False
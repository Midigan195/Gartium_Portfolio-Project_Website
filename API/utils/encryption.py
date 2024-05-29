"""
Module: utils/encryption.py

This module provides functions for hashing and verifying passwords using bcrypt.
"""

from bcrypt import hashpw, gensalt, checkpw

def hash_password(password):
    """
    Hashes a password using bcrypt.

    Args:
        password (str): The password to hash.

    Returns:
        str: The hashed password.
    """
    hashed_password = hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')
    return hashed_password

def verify_password(password, hashed_password):
    """
    Verifies a password against a hashed password using bcrypt.

    Args:
        password (str): The password to verify.
        hashed_password (str): The hashed password to compare against.

    Returns:
        bool: True if the password matches the hashed password, False otherwise.
    """
    return checkpw(password.encode('utf-8'), hashed_password)
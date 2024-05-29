"""
Module: utils/formatting.py

This module provides functions for formatting data, such as views counts.
"""

def format_views(views):
    """
    Formats the number of views into a more human-readable form.

    Args:
        views (int): The number of views to format.

    Returns:
        str: The formatted views count.
    """
    if views >= 1000000000:
        return f"{views // 1000000000}B"
    elif views >= 1000000:
        return f"{views // 1000000}M"
    elif views >= 1000:
        return f"{views // 1000}.{views // 100 % 10}K"
    else:
        return str(views)
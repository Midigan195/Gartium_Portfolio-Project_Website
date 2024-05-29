"""
Module: garlium_db/db.py

This module provides functions for managing database connections using MySQL Connector/Python.
"""

from flask import g
from mysql.connector import pooling

host = "Mirigan.mysql.pythonanywhere-services.com"
user = "Mirigan"
password = "Enirboreh"
database = "Mirigan$Garlium_db"
DB_POOL = pooling.MySQLConnectionPool(
    pool_name="GarliumDBPool",
    pool_size=4,
    pool_reset_session=True,
    host=host,
    user=user,
    password=password,
    database=database
)

def get_db():
    """
    Get a database connection from the connection pool.

    Returns:
        MySQLConnection: A connection to the database.
    """
    # Check if 'db' is not in the g object or the connection is closed
    if 'db' not in g or not g.db.is_connected():
        try:
            # If not, obtain a new connection from the connection pool
            g.db = DB_POOL.get_connection()
        except pooling.PoolError as e:
            # Handle connection pool exhaustion or other errors
            print("Error obtaining connection from pool:", e)
            raise
    return g.db

def close_db(e=None):
    """
    Close the database connection.

    Args:
        e: An exception that occurred, if any.
    """
    # Pop the 'db' connection from the g object and close it if it exists
    db = g.pop('db', None)
    if db is not None:
        db.close()

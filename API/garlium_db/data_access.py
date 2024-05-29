"""
Module: garlium_db/data_access.py

This module provides functions for accessing and manipulating data in the Garlium database.
"""

import uuid
from utils.encryption import verify_password
from utils.formating import format_views
from garlium_db.db import get_db, close_db

def add_user_to_database(username, password, email):
    """
    Adds a new user to the database.

    Args:
        username (str): The username of the new user.
        password (str): The password of the new user (hashed).
        email (str): The email address of the new user.

    Returns:
        int: Status code indicating the result of the operation:
             - 0: Success
             - 1: Username already exists
             - 2: Email already exists
             - 3: Error occurred during database operation
    """
    try:
        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT username, email FROM Users WHERE username = %s OR email = %s LIMIT 1", (username, email))
        existing_user = cursor.fetchone()
        if existing_user:
            if existing_user[0] == username:
                cursor.close()
                close_db()
                return 1
            else:
                cursor.close()
                close_db()
                return 2

        user_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO Users (user_id, email, username, password_hash) VALUES (%s, %s, %s, %s)",
                       (user_id, email, username, password))
        db.commit()
        cursor.close()
        close_db()
        return 0
    except Exception:
        cursor.close()
        close_db()
        return 3

def validate_user_credentials(username, password):
    """
    Validates user credentials against the database.

    Args:
        username (str): The username of the user.
        password (str): The password of the user.

    Returns:
        str or None: The user ID if credentials are valid, None otherwise.
    """
    db = None
    cursor = None
    if not username or not password:
        cursor.close()
        close_db()
        return False
    try:
        db = get_db()
        cursor = db.cursor()

        # Fetch only the password hash for the provided username
        cursor.execute("SELECT user_id, password_hash FROM Users WHERE username = %s LIMIT 1", (username,))
        user_data = cursor.fetchone()

        if user_data:
            # If user exists, validate the password
            user_id, stored_password_hash = user_data
            if verify_password(password, stored_password_hash):
                cursor.close()
                close_db()
                return user_id  # Password is valid
            else:
                cursor.close()
                close_db()
                return None  # Password is incorrect
        else:
            cursor.close()
            close_db()
            return None  # User doesn't exist

    except Exception:
        cursor.close()
        close_db()
        return None  # Error occurred during database query

def check_user_exist(user_id):
    """
    Checks if a user exists in the database.

    Args:
        user_id (str): The ID of the user to check.

    Returns:
        bool: True if the user exists, False otherwise.
    """
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT EXISTS(SELECT 1 FROM Users WHERE user_id = %s)", (user_id,))
        user_exists = cursor.fetchone()[0]

        cursor.close()
        close_db()

        return user_exists

    except Exception:
        cursor.close()
        close_db()
        return False

def add_post_to_database(user_id, title, tags, content, post_url, public_id):
    """
    Adds a new post to the database.

    Args:
        user_id (str): The ID of the user creating the post.
        title (str): The title of the post.
        tags (str): The tags associated with the post.
        content (str): The content of the post.
        post_url (str): The URL of the post.
        public_id (str): The public ID of the post.

    Returns:
        str or None: The ID of the newly created post if successful, None otherwise.
    """
    try:
        db = get_db()
        cursor = db.cursor()

        post_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO Post (post_id, user_id, title, tags, content, post_url, public_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (post_id, user_id, title, tags, content, post_url, public_id))
        db.commit()
        cursor.close()
        close_db()

        return post_id

    except Exception:
        cursor.close()
        close_db()
        return None

def get_posts_for_page(page_number=1, page_size=3, search=None, search_filter=None):
    """
    Retrieves posts for a specific page from the database.

    Args:
        page_number (int): The page number to retrieve.
        page_size (int): The number of posts per page.
        search (str): The search term to filter posts (optional).
        search_filter (str): The type of search filter to apply (optional).

    Returns:
        list or None: A list of dictionaries containing post information if successful, None otherwise.
    """
    db = None
    cursor = None
    try:
        db = get_db()
        cursor = db.cursor()
        offset = (page_number - 1) * page_size

        if search:
            if search_filter == "tag":
                query = """
                    SELECT Post.post_id, Post.views, Post.title, Post.post_url, Users.username
                    FROM Post
                    JOIN Users ON Post.user_id = Users.user_id
                    WHERE Post.tags LIKE CONCAT('%', %s, '%')
                    ORDER BY Post.post_id DESC
                    LIMIT %s OFFSET %s
                """
                cursor.execute(query, ('%' + search + '%', page_size, offset))
            elif search_filter == "user":
                query = """
                    SELECT Post.post_id, Post.views, Post.title, Post.post_url, Users.Username
                    FROM Post
                    JOIN Users ON Post.user_id = Users.user_id
                    WHERE Users.username LIKE %s
                    ORDER BY Post.post_id DESC
                    LIMIT %s OFFSET %s
                """
                cursor.execute(query, ('%' + search + '%', page_size, offset))
            else:
                query = """
                    SELECT Post.post_id, Post.views, Post.title, Post.post_url, Users.Username
                    FROM Post
                    JOIN Users ON Post.user_id = Users.user_id
                    WHERE Post.title LIKE %s
                    ORDER BY Post.post_id DESC
                    LIMIT %s OFFSET %s
                """
                cursor.execute(query, ('%' + search + '%', page_size, offset))
        else:
            cursor.execute("""
                SELECT Post.post_id, Post.views, Post.title, Post.post_url, Users.Username
                FROM Post
                JOIN Users ON Post.user_id = Users.user_id
                ORDER BY Post.post_id DESC
                LIMIT %s OFFSET %s
            """, (page_size, offset))

        rows = cursor.fetchall()
        posts = [
            {
                'post_id': row[0],
                'views': format_views(row[1]),
                'title': row[2],
                'image_url': row[3],
                'username': row[4]
            }
            for row in rows
        ]

        cursor.close()
        close_db()
        return posts

    except Exception:
        cursor.close()
        close_db()
        return None

def get_post_content(post_id, user_id):
    """
    Retrieves the content of a specific post from the database and updates its view count.

    Args:
        post_id (str): The ID of the post to retrieve.
        user_id (str): The ID of the user viewing the post.

    Returns:
        dict or None: A dictionary containing post information if successful, None otherwise.
    """
    try:
        db = get_db()
        cursor = db.cursor()

        # Increment views count
        cursor.execute("""
            UPDATE Post
            SET views = views + 1
            WHERE post_id = %s
        """, (post_id,))
        db.commit()  # Commit the update

        sql_query = """
            SELECT p.title, p.tags, p.content, p.post_url, p.views, u.username,
                   (SELECT COUNT(*) FROM Likes WHERE post_id = p.post_id) AS likes, p.public_id, p.user_id,
                   (SELECT EXISTS(SELECT 1 FROM Likes WHERE user_id = %s AND post_id = %s)) AS liked
            FROM Post p
            INNER JOIN Users u ON p.user_id = u.user_id
            WHERE p.post_id = %s
            LIMIT 1
        """
        cursor.execute(sql_query, (user_id, post_id, post_id))
        post_tuple = cursor.fetchone()
        delete_url = None
        if post_tuple[8] == user_id:
            delete_url = f"https://mirigan.pythonanywhere.com/post/delete/{post_tuple[7]}?user_id={user_id}"
        like_url = f"https://mirigan.pythonanywhere.com/add_like?user_id={user_id}&post_id={post_id}"

        if post_tuple:
            post_dict = {
                'title': post_tuple[0],
                'tags': post_tuple[1],
                'content': post_tuple[2],
                'post_url': post_tuple[3],
                'views': format_views(post_tuple[4]),
                'username': post_tuple[5],
                'likes': post_tuple[6],
                'delete_url': delete_url,
                'liked': post_tuple[9],
                'like_url': like_url
            }
        cursor.close()
        close_db()
        return post_dict

    except Exception:
        cursor.close()
        close_db()

def toggle_like(user_id, post_id):
    """
    Toggles the like status for a post by a specific user.

    Args:
        user_id (str): The ID of the user.
        post_id (str): The ID of the post.

    Returns:
        str or bool: A success message if successful, False otherwise.
    """
    try:
        db = get_db()
        cursor = db.cursor()

        # Check if the like already exists
        cursor.execute("SELECT COUNT(*) FROM Likes WHERE user_id = %s AND post_id = %s", (user_id, post_id))
        like_count = cursor.fetchone()[0]

        if like_count == 0:
            # If the like does not exist, add a new like
            cursor.execute("INSERT INTO Likes (user_id, post_id) VALUES (%s, %s)", (user_id, post_id))
            res = f"User {user_id} liked Post {post_id} successfully"
        else:
            # If the like already exists, remove it (unlike)
            cursor.execute("DELETE FROM Likes WHERE user_id = %s AND post_id = %s", (user_id, post_id))
            res = f"User {user_id} unliked Post {post_id} successfully"

        db.commit()
        cursor.close()
        close_db()
        return res

    except Exception:
        if cursor:
            cursor.close()
        close_db()
        return False

def check_like_status(user_id, post_id):
    """
    Checks the like status of a user for a specific post.

    Args:
        user_id (str): The ID of the user.
        post_id (str): The ID of the post.

    Returns:
        bool: True if the user has liked the post, False otherwise.
    """
    try:
        db = get_db()
        cursor = db.cursor()

        # Check if the like already exists using EXISTS
        cursor.execute("SELECT EXISTS(SELECT 1 FROM Likes WHERE user_id = %s AND post_id = %s)", (user_id, post_id))
        like_exists = cursor.fetchone()[0]

        cursor.close()
        close_db()
        return like_exists

    except Exception:
        if cursor:
            cursor.close()
        close_db()
        return False

def check_and_delete_post(user_id, public_id):
    """
    Checks if the current user is the owner of the post with the given public ID and deletes it if they are.

    Args:
        user_id (str): The ID of the user.
        public_id (str): The public ID of the post to be checked and deleted.

    Returns:
        bool: True if the post is successfully deleted, False otherwise.
    """
    try:
        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            SELECT Post.post_id
            FROM Post
            INNER JOIN Users ON Post.user_id = Users.user_id
            WHERE Post.public_id = %s AND Users.user_id = %s
        """, (public_id, user_id))

        result = cursor.fetchone()
        if not result:
            cursor.close()
            close_db()
            return False

        post_id = result[0]
        cursor.execute("DELETE FROM Post WHERE post_id = %s", (post_id,))
        db.commit()

        cursor.close()
        close_db()
        return True

    except Exception:
        db.rollback()
        cursor.close()
        close_db()
        return False
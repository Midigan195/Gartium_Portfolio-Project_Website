from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from utils.cloudinary_utils import upload_image, delete_image
from utils.error import generate_error_response
from utils.encryption import hash_password
from utils.image_upload import validate_image
from forms import UploadForm, SignUpForm
from garlium_db.db import get_db, close_db
from garlium_db.data_access import (
    add_user_to_database,
    validate_user_credentials,
    check_user_exist,
    add_post_to_database,
    get_posts_for_page,
    get_post_content,
    toggle_like,
    check_like_status,
    check_and_delete_post
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'eb9d81a1b0b2f7b6f21aa4d4'
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def upload_form():
    """
    Renders the HTML upload form using the upload.html template.
    """
    form = UploadForm()
    return render_template('upload.html', form=form)

@app.route('/login', methods=['POST'])
def login():
    """
    Authenticates users by checking their credentials (username and password) against the database.

    Returns:
        JSON: User ID if authentication is successful, error message otherwise.
    """
    username = request.json.get('username')
    password = request.json.get('password')

    user_id = validate_user_credentials(username, password)

    if user_id:
        return jsonify({'user_id': user_id}), 200
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/signup', methods=['POST'])
def signup():
    """
    Registers new users by validating the signup form data and adding the user to the database if the data is valid.

    Returns:
        JSON: Success message if registration is successful, error message otherwise.
    """
    form = SignUpForm()

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        # Your signup logic using SignupForm data
        # Example: Create a new user in the database

        response_data = {
            'message': 'Signup successful',
            'username': username,
            'email': email,
            'password': hash_password(password)
        }
        resp = add_user_to_database(response_data['username'], response_data['password'], response_data['email'])
        if resp == 1:
            return jsonify({'error': 'Username already exist'}), 500
        elif resp == 2:
            return jsonify({'error': 'This email is already in use'}), 500
        elif resp == 3:
            return jsonify({'error': 'Failed to register user'}), 500
        return jsonify(response_data), 200

    return generate_error_response(form)

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Handles the uploading of files, such as images, to the server.

    Returns:
        JSON: Success message with the post ID if the upload is successful, error message otherwise.
    """
    form = UploadForm()

    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No selected file'}), 400

    if form.validate_on_submit():
        title = form.title.data
        tags = form.tags.data
        description = form.description.data
        user_id = form.user_id.data

        if not validate_image(file): return jsonify({'error': 'Invalid file type. Only JPEG and PNG images are allowed.'}), 400
        if not check_user_exist(user_id): return jsonify({'error': 'Invalid user ID'}), 400

        result = upload_image(file)  # Process the data
        if result is None:
                return jsonify({'error': 'Failed to upload image to server'}), 500

        url = result.get('secure_url')
        public_id = result.get('public_id')

        post_id = add_post_to_database(user_id, title, tags, description, url, public_id)
        if post_id is None:
            return jsonify({'error': 'Failed to add post to database'}), 500
        return jsonify({'post_id': post_id}), 200

    return generate_error_response(form)

@app.route('/post/delete/<public_id>', methods=['DELETE']) #GET method is only temporary chnage to delete as soon as possible
def delete_file(public_id):
    """
    Handles the deletion of a post along with its associated image from the server.

    Args:
        public_id (str): The public ID of the post to be deleted.

    Returns:
        JSON: Success message if the deletion is successful, error message otherwise.
    """
    user_id = request.args.get('user_id')

    if not (public_id and user_id):
        return jsonify({'error': 'Missing public_id or user_id parameters'}), 400

    if not check_user_exist(user_id):
        return jsonify({'error': 'User does not exist'}), 400

    image_delete = delete_image(public_id)
    if not image_delete:
        return jsonify({'error': 'Failed to delete image'}), 400

    delete_result = check_and_delete_post(user_id, public_id)
    if not delete_result:
        return jsonify({'error': 'Failed to delete post'}), 400

    return jsonify({public_id: "item removed"}), 200

@app.route('/post-view', methods=['GET'])
def post_view():
    """
    Retrieves the content of a specific post based on its ID.

    Returns:
        JSON: Content of the post including title, tags, content, views, username, likes, 
        delete URL (if the user is the author), and whether the user has liked the post.
    """
    user_id = request.args.get('user_id')
    post_id = request.args.get('post_id')

    if user_id is None or post_id is None:
        return jsonify({'error': 'Invalid user_id or post_id'}), 400

    if len(user_id) != 36 or len(post_id) != 36:
        return jsonify({'error': 'Invalid user_id or post_id'}), 400

    content = get_post_content(post_id, user_id)
    if content is None:
        return jsonify({'error': 'Content not found for the given post_id'}), 404
    return jsonify(content), 200


@app.route('/feed', methods=['GET'])
def get_posts():
    """
    Retrieves a list of posts for a given page number, with optional search and filter parameters.

    Returns:
        JSON: List of posts including their IDs, views, titles, image URLs, and usernames.
    """
    page_number = int(request.args.get('page', '1') or '1')
    search = request.args.get('search', None)
    search_filter = request.args.get('filter', None)
    posts = get_posts_for_page(page_number, 15, search, search_filter)

    if posts is None:
        return jsonify({'error': 'Failed to retrieve posts'}), 500
    return jsonify(posts), 200

@app.route('/add_like', methods=['POST'])
def add_like_route():
    """
    Toggles the like status of a post for a given user.

    Returns:
        JSON: Success message if the like status is updated successfully, error message otherwise.
    """
    user_id = request.args.get('user_id')
    post_id = request.args.get('post_id')

    if user_id is None or post_id is None:
        return jsonify({'error': 'Invalid user_id or post_id'}), 400

    if len(user_id) != 36 or len(post_id) != 36:
        return jsonify({'error': 'Invalid user_id or post_id'}), 400

    message = toggle_like(user_id, post_id)
    if not message:
        return jsonify({'error': 'Failed to add like'}), 500

    return jsonify({'message': message}), 200

@app.route('/check_like', methods=['GET'])
def check_like():
    """
    Checks whether a user has liked a specific post.

    Returns:
        JSON: True if the user has liked the post, False otherwise.
    """
    user_id = request.args.get('user_id')
    post_id = request.args.get('post_id')

    if user_id is None or post_id is None:
        return jsonify({'error': 'Invalid user_id or post_id'}), 400
    if len(user_id) != 36 or len(post_id) != 36:
        return jsonify({'error': 'Invalid user_id or post_id'}), 400

    liked = check_like_status(user_id, post_id)
    return jsonify({'liked': liked})


if __name__ == '__main__':
    app.run(debug=True)
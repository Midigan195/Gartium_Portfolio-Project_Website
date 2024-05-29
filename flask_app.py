from flask import Flask, request, session, redirect, url_for, jsonify, render_template, make_response
import requests  # Import requests module
from functools import wraps

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

session_obj = requests.Session()

def login_required(f):     # use decorator when the user needs to be authenticated to view a page else redirect to login
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('do_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def clear_cookies():   #Clear all cookies and valid sessions(user has lo login again)
    return redirect(url_for('load_feed'))

@app.route('/login', methods=['GET', 'POST'])
def do_login():


    if 'username' in session:
            return redirect(url_for('load_feed'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        login_data = {'username': username, 'password': password}
        response = session_obj.post('https://mirigan.pythonanywhere.com/login', json=login_data)

        if response.status_code == 200:
            user_id = response.json().get('user_id')
            session['user_id'] = user_id
            session['username'] = username
            return redirect(url_for('load_feed'))
        else:
            return render_template('login.html', error='Login failed. Please try again.')

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def do_signup():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        login_data = {'username': username, 'password': password, 'email': email}
        response = session_obj.post('https://mirigan.pythonanywhere.com/signup', json=login_data)

        if response.status_code == 200:
            return redirect(url_for('do_login'))
        else:
            return render_template('signup.html', error='Signup failed. Please try again.')

    return render_template('signup.html')

@app.route('/home')
@login_required
def load_feed():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/upload')
@login_required
def upload_post():
    user_id = session['user_id']
    return render_template('upload.html', user_id=user_id)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/post', methods=['GET'])
@login_required
def view_post():
    post_id = request.args.get('post_id')
    user_id = session["user_id"]
    if post_id:
        api_url = f'http://mirigan.pythonanywhere.com/post-view?post_id={post_id}&user_id={user_id}'
        response = requests.get(api_url)
        if response.status_code == 200:
            post_data = response.json()
            rendered_html = render_template('viewer.html', post_data=post_data)
            resp = make_response(rendered_html)
            resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            resp.headers['Pragma'] = 'no-cache'
            resp.headers['Expires'] = '0'
            return resp
        else:
            return render_template('404.html')
    return render_template('404.html')


if __name__ == '__main__':
    app.run(debug=True)


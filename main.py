import base64
import io
import os
import pickle
import gc
from functools import wraps
from PIL import Image

from dotenv import load_dotenv
from flask import Flask, render_template, request, session, redirect, \
    url_for, flash, Response, send_file, jsonify
from werkzeug.utils import secure_filename

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(PROJECT_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'jpeg', 'jpg', 'png', 'tiff', 'gif'}
PICKLE_FILE = 'image_mapping.pickle'

app = Flask(__name__)


def check_extension(filename):
    # split the filename by '.' and get the extension
    ext = filename.split(".")[1]
    if ext.lower() in ALLOWED_EXTENSIONS:
        return True
    return False


def get_response_image(image_path):
    pil_img = Image.open(image_path, mode='r')
    byte_arr = io.BytesIO()
    pil_img.save(byte_arr, format='PNG')
    encoded_img = base64.encodebytes(byte_arr.getvalue()).decode('ascii')
    return encoded_img


def get_pickle_file():
    # Get the path of pickle file
    pickle_file_path = os.path.join(PROJECT_DIR, PICKLE_FILE)
    image_map = {}
    # if pickle file exists return the loaded object
    # else return empty dictionary.
    if os.path.exists(pickle_file_path):
        with open(pickle_file_path, 'rb') as f:
            image_map = pickle.load(f)
    return image_map


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        # checks if `authenticated` keyword is present in session
        # means if the user is logged in or not.
        # if yes, return the passed function
        if 'authenticated' in session:
            return f(*args, **kwargs)
        else:
            # redirect to the login URL with a flash message
            flash("You need to login first")
            return redirect(url_for('login'))

    return wrap


@app.route('/', methods=['GET', 'POST'])
def login():
    # Check if incoming request method is POST
    if request.method == 'POST':
        # Fetch the username and password input by the user
        user = request.form['username']
        password = request.form['password']

        # Verify the username and password
        if user == os.getenv('USER_NAME') \
                and password == os.getenv('PASSWORD'):
            session['authenticated'] = True
            # redirect to homepage
            session['username'] = user
            return redirect(url_for('homepage'))
        else:
            error = "Invalid Username / Password"
        gc.collect()
        # return to login page with error message.
        return render_template('login.html', error=error)

    # If the request method is GET, simply return login page.
    return render_template('login.html')


@app.route('/homepage/')
@login_required
def homepage():
    return render_template('homepage.html')


@app.route('/upload/', methods=['POST'])
@login_required
def upload_image():
    # Verify the request method and check if it has files or not
    if request.method == 'POST' and ('file' not in request.files):
        return Response('No file part')
    file = request.files['file']
    if file.filename == '':
        return Response('No selected file')

    # Get the pickle object
    image_map = get_pickle_file()
    # Get the mapped name for the image
    name = request.form['image_name'].lower()
    if image_map.get(name, None):
        return Response("This name is already used! Please use another name",
                        status=400)

    # Check if the `uploads` folder exists
    if not os.path.exists(os.path.join(PROJECT_DIR, 'uploads')):
        os.mkdir(os.path.join(PROJECT_DIR, 'uploads'))

    if file and check_extension(file.filename):
        filename = secure_filename(file.filename)
        # Path to store the file
        file_path = os.path.join(UPLOADS_DIR, filename)
        # Store the uploaded file
        file.save(file_path)
        # Update the image_map object
        image_map[name] = file_path
        # Store the object
        with open(os.path.join(PROJECT_DIR, PICKLE_FILE), 'wb') as f:
            pickle.dump(image_map, f)
        return Response("File uploaded", status=200)
    # only return if the uploaded file format is not in the ALLOWED_EXTENSION
    return Response("File Format not supported!", status=403)


@app.route('/search/', methods=['POST'])
@login_required
def search():
    image_name = request.form['search_text'].lower()
    image_map = get_pickle_file()
    path = image_map.get(image_name, None)
    if image_map and path:
        encoded_image = get_response_image(path)
        data = {'image_data': encoded_image}
        return jsonify(data)
    else:
        return Response("No Image found", status=400)


@app.route('/logout/')
@login_required
def logout():
    # clear the session
    session.clear()
    # flash("You are logged out")
    gc.collect()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.secret_key = os.getenv('SECRET_KEY')
    app.run(host='0.0.0.0', port=5000, debug=True)

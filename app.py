import os
from flask import Flask, redirect, request, session, jsonify
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
import json
from flask_session import Session  # Import the Flask-Session extension
from flask_cors import CORS
import requests
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64
from google.oauth2.credentials import Credentials
import re
import hashlib
import jwt
import datetime

app = Flask(__name__)

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = os.urandom(24)

Session(app)
CORS(app)

client_secret = json.load(open('client_secret.json'))

CLIENT_ID = client_secret['web']['client_id']
SCOPE = 'https://mail.google.com/'
REDIRECT_URI = 'https://localhost:5000/callback/'
ACCESS_TOKEN_INFO = 'https://www.googleapis.com/oauth2/v1/tokeninfo'

TOKEN_FILE = 'user_tokens.json'
SECRET_KEY = 'devnet+project'

flow = Flow.from_client_secrets_file(
    'client_secret.json',
    scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email', SCOPE],
    redirect_uri=REDIRECT_URI,
    # access_type='oftine' # Doesn't work
)


@app.route("/login-google", methods=['POST'])
def login_google():
    req_data = request.get_json()
    token = req_data['token']
    client_id = req_data['client_id']
    id_info = id_token.verify_oauth2_token(token, Request(), client_id)
    user_email = id_info.get('email', 'Email not available')

    return jsonify(user_email)


@app.route('/login', methods=['POST'])
def login():
    req_data = request.get_json()
    email = req_data['email']
    password = req_data['password']

    try:
        with open("./data/users.json", 'r') as file:
            file_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return jsonify({'error': 'No registered users'}), 401

    for user in file_data["users"]:
        if user["email"] == email:
            stored_password = user["password"]
            input_password = hash_password(password)

            if stored_password == input_password:
                payload = {
                    'email': email,
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
                }
                token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
                return jsonify({'token': token}), 200

    return jsonify({'error': 'Invalid credentials'}), 401


@app.route('/register', methods=["POST"])
def register():
    req_data = request.get_json()
    email = req_data['email']
    password = req_data['password']

    if not is_valid(email):
        return jsonify({
            'status': '422',
            'res': 'failure',
            'error': 'Invalid email format. Please enter a valid email address'
        })

    hash_pass = hash_password(password)

    result = save_user({
        "email": email,
        "password": hash_pass
    })

    if result:
        return jsonify({"email": email}), 201
    else:
        return jsonify({'error': 'User with the same email already exists'}), 409


@app.route('/callback/')
def callback():
    state = session['state']
    flow.fetch_token(authorization_response=request.url)

    if 'error' in request.args:
        return 'Error: ' + request.args['error']

    id_info = id_token.verify_oauth2_token(flow.credentials.id_token, Request(), CLIENT_ID)
    user_email = id_info.get('email', 'Email not available')

    tokens = {}
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as file:
            tokens = json.load(file)

    tokens[user_email] = flow.credentials.to_json()
    with open(TOKEN_FILE, 'w') as file:
        json.dump(tokens, file)
    callback.flow = flow

    session['user_email'] = user_email
    return f'Logged in as: {user_email}'


@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    user_email = session.get('user_email')

    with open(TOKEN_FILE, 'r') as user_tokens_json:
        user_tokens = json.load(user_tokens_json)

    try:
        token = json.loads(user_tokens[user_email])[
            'token']
        token_response = requests.get(url=ACCESS_TOKEN_INFO, params=f'access_token={token}').json()
    except:
        return jsonify({'valid': False})

    if token_response['email'] == user_email:
        return jsonify({'valid': True, 'email': user_email})
    else:
        return jsonify({'valid': False})


@app.route('/api/send-email', methods=['POST'])
def send_email():
    data = request.json
    with open(TOKEN_FILE, 'r') as user_tokens_json:
        user_tokens = json.load(user_tokens_json)

    try:
        user_email = check_auth().json['email']
    except:
        return 'cookie/token error'
    token = json.loads(user_tokens[user_email])

    credentials = Credentials.from_authorized_user_info(token)
    service = build('gmail', 'v1', credentials=credentials)  # Missing refresh cookie because acces type is not offline

    message = MIMEText(data['text'], 'html')
    message['to'] = data['to']
    message['subject'] = data['subject']
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

    service.users().messages().send(
        userId='me',
        body={'raw': raw_message}
    ).execute()


def hash_password(password):
   password_bytes = password.encode('utf-8')
   hash_object = hashlib.sha256(password_bytes)
   return hash_object.hexdigest()


def is_valid(email):
    regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
    if re.fullmatch(regex, email):
      return True
    else:
      return False


def user_exists(email, users):
    for user in users:
        if user["email"] == email:
            return True
    return False


def save_user(user):
    try:
        with open("./data/users.json", 'r') as file:
            # First, attempt to load existing data from the file.
            file_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # If the file doesn't exist or is empty, initialize it with an empty "users" list.
        file_data = {"users": []}

    # Check if the user with the same email already exists.
    if not user_exists(user["email"], file_data["users"]):
        # If the user doesn't exist, append the new user as a dictionary to the "users" list.
        file_data["users"].append({"email": user["email"], "password": user["password"]})

        # Open the file in write mode and write the updated data back to it.
        with open("./data/users.json", 'w') as file:
            json.dump(file_data, file, indent=4)
        return True
    else:
        return False



if __name__ == '__main__':
    app.run(port=8080,debug=True)
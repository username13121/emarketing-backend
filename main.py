import os
from flask import Flask, redirect, request, session, jsonify
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
import json
from flask_session import Session  # Import the Flask-Session extension
import requests
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64
from google.oauth2.credentials import Credentials

app = Flask(__name__)

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = os.urandom(24)

Session(app)

client_secret = json.load(open('client_secret.json'))

CLIENT_ID = client_secret['web']['client_id']
SCOPE = 'https://mail.google.com/'
REDIRECT_URI = 'https://localhost:5000/callback/'
ACCESS_TOKEN_INFO = 'https://www.googleapis.com/oauth2/v1/tokeninfo'

TOKEN_FILE = 'user_tokens.json'

flow = Flow.from_client_secrets_file(
    'client_secret.json',
    scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email', SCOPE],
    redirect_uri=REDIRECT_URI,
    # access_type='offline' # Doesn't work
)


@app.route('/')
def index():
    return redirect('/login', code=302)


@app.route('/login')
def login():
    authorization_url, state = flow.authorization_url()
    session['state'] = state
    return redirect(authorization_url)


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


if __name__ == '__main__':
    app.run(ssl_context='adhoc', debug=True)

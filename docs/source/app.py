import os
from flask import Flask, redirect, request, session, jsonify
import json
from flask_session import Session
import requests
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64
from google.oauth2.credentials import Credentials

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = os.urandom(24)
Session(app)

CLIENT_SECRET = json.load(open('client_secret.json'))['web']

def get_email():
    # """
    # Get email from Google API
    #
    # :param string session['email']:
    #
    # :return: email
    #
    # """
    token_data = requests.get(url='https://www.googleapis.com/oauth2/v1/tokeninfo',
                              params=f'access_token={session["access_token"]}').json()
    return token_data['email']


def set_user_info(refresh_token):

    # """
    # Gets access and id tokens by refresh token and sets it as a session variable
    #
    # :param string refresh_token:
    # :return:
    # """
    tokens = requests.post('https://oauth2.googleapis.com/token',
                           params={
                               'client_id': CLIENT_SECRET['client_id'],
                               'client_secret': CLIENT_SECRET['client_secret'],
                               'grant_type': 'refresh_token',
                               'refresh_token': refresh_token}).json()
    try:
        session['id_token'] = tokens['id_token']
        session['access_token'] = tokens['access_token']
        session['refresh_token'] = refresh_token
        session['email'] = get_email()
        return True
    except:
        return False


def check_access_token():
    try:
        get_email()
        return True
    except:
        return False


def get_access_token():
    try:
        access_token = session['access_token']
        if check_access_token():
            return access_token
    except:
        pass

    if set_user_info(session['refresh_token']):
        return session['access_token']
    else:
        return False


@app.route('/register', methods=['POST'])
def register():

    """
    This route is for registration of new users. It sets user info in the session

:param refresh_token:

:return: success: true/false, cookies{session}

Required request format:

.. code-block:: http

    POST /register HTTP/1.1
    Content-Type: application/json
    Content-Length: 124

    {"refresh_token": "1//0cVS9kIaHwPb_CgYIARAAGAwSNwF-L9Ira2i9rNPs3tyyzlk-yssv2Uwwv-tSxHoMBmB73ZI62hhbYHdXimIP266fFtPAgigbEWw"}

Expected response:

.. code-block:: http

    HTTP/1.1 200 OK
    Server: Werkzeug/3.0.1 Python/3.11.3
    Date: Sun, 12 Nov 2023 18:34:44 GMT
    Content-Type: application/json
    Content-Length: 22
    Set-Cookie: session=3006a9d2-11f2-4ffc-958d-89e0e92abec7; Expires=Wed, 13 Dec 2023 18:34:44 GMT; HttpOnly; Path=/
    Connection: close

    { "success": true }



    """
    refresh_token = request.get_json()['refresh_token']
    if set_user_info(refresh_token):
        return jsonify({'success': True})
    else:
        return jsonify({'success': False})


# def change_request(req):
#     try:
#         session['access_token']=req['access_token']
#     except:
#         pass
#     try:
#         session['refresh_token'] = req['refresh_token']
#     except:
#         pass
#     try:
#         session['email'] = req['email']
#     except:
#         pass


@app.route('/login', methods=['GET'])
def login():

    """
    This route is for authorizing registered users. It checks user's cookies and returns email

:param cookies{session}:

:return: success: true/false, email

Required request format:

.. code-block:: http

    GET /login HTTP/1.1
    Cookie: session=9b2e5bc4-a550-4903-b396-cd3305de4b76

Expected response:

.. code-block:: http

    HTTP/1.1 200 OK
    Server: Werkzeug/3.0.1 Python/3.11.3
    Date: Sun, 12 Nov 2023 19:29:13 GMT
    Content-Type: application/json
    Content-Length: 64
    Set-Cookie: session=9b2e5bc4-a550-4903-b396-cd3305de4b76; Expires=Wed, 13 Dec 2023 19:29:13 GMT; HttpOnly; Path=/
    Connection: close

    { "email": "username12312355@gmail.com",
    "successs": true }



    """

    # change_request(request.get_json())
    try:
        if get_access_token():
            return jsonify({'successs': True,
                            'email': session['email']})
    except:
        pass
    return jsonify({'success': False})


@app.route('/get-link', methods=['GET'])
def get_link():
    redirect_uri = request.get_json()['redirect_uri']

    link = Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://mail.google.com/'],
        redirect_uri=redirect_uri
    ). \
        authorization_url(access_type='offline',
                          include_granted_scopes='true',
                          prompt='consent')
    return jsonify({'authorization_link': link[0]})


if __name__ == '__main__':
    app.run(debug=True)

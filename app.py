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
    token_data = requests.get(url='https://www.googleapis.com/oauth2/v1/tokeninfo',
                              params=f'access_token={session["access_token"]}').json()
    return token_data['email']


def set_user_info(refresh_token):
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
        access_token=session['access_token']
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
    #change_request(request.get_json())
    try:
        if get_access_token():
            return jsonify({'successs': True,
                            'email': session['email']})
    except:
        pass
    return jsonify({'success': False})

@app.route('/get-link', methods=['GET'])
def get_link():
    redirect_uri=request.get_json()['redirect_uri']

    link = Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://mail.google.com/'],
        redirect_uri=redirect_uri
    ).\
        authorization_url(access_type='offline',
                          include_granted_scopes='true',
                          prompt='consent')
    return jsonify({'authorization_link': link[0]})


if __name__ == '__main__':
    app.run(debug=True)
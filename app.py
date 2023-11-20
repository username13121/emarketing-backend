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
import db
from psycopg2.extras import execute_values

app = Flask(__name__)

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = os.urandom(24)

Session(app)
CLIENT_SECRET = json.load(open('client_secret.json'))['web']


def check_db():
    try:
        if db.list_table() == ['sender', 'receivers']:
            return True
        else:
            db.create_table()
            return check_db()
    except:
        return False


if check_db():
    print('Database ok')
else:
    print('Database error')


def add_sender(sender):
    try:
        db.cursor.execute(
            f'INSERT INTO sender(email) VALUES (\'{sender}\')'
            'ON CONFLICT DO NOTHING')
        return True
    except:
        return False


def get_id(sender):
    try:
        db.cursor.execute(
            f'SELECT senderId FROM sender WHERE email=\'{sender}\'')
        return db.cursor.fetchone()[0]
    except:
        return False


def get_receivers(sender):
    try:
        db.cursor.execute(
            f'SELECT email FROM receivers WHERE senderId=\'{get_id(sender)}\'')
        return [i[0] for i in db.cursor.fetchall()]
    except:
        return False


def add_receivers(sender, receivers):
    try:
        sender = get_id(sender)
        receivers = [(sender, i) for i in receivers]
        execute_values(db.cursor, 'INSERT INTO receivers VALUES %s'
                                  'ON CONFLICT DO NOTHING',
                       receivers)
        return True
    except:
        return False


def delete_receivers(sender, receivers):
    print(tuple(receivers))
    try:
        sender = get_id(sender)
        db.cursor.execute(
        f'DELETE FROM receivers WHERE senderId = {sender} AND email in {tuple(receivers)}'
        )
        return True
    except:
        return False


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
    refresh_token = request.get_json()['refresh_token']
    if set_user_info(refresh_token):
        add_sender(session['email'])
        return jsonify({'success': True})
    else:
        return jsonify({'success': False})


def change_request(req):
    try:
        session['access_token'] = req['access_token']
    except:
        pass
    try:
        session['refresh_token'] = req['refresh_token']
    except:
        pass
    try:
        session['email'] = req['email']
    except:
        pass


@app.route('/login', methods=['GET'])
def login():
    # change_request(request.get_json())
    try:
        if get_access_token():
            return jsonify({'successs': True,
                            'email': session['email']})
    except:
        pass
    return jsonify({'success': False})

@app.route('/receivers', methods=['POST', 'GET'])
def receivers_route():
    if request.method=='GET':
        try:
            return jsonify({
                'success': True,
                'receivers': get_receivers(session['email'])
            })
        except:
            return jsonify({
                'success': False
            })
    else:
        try:
            add=add_receivers(session['email'], request.get_json()['add'])
        except:
            add=False
        try:
            delete=delete_receivers(session['email'], request.get_json()['delete'])
        except:
            delete=False
        return jsonify({
            'success_add': add,
            'success_delete': delete
        })


# @app.route('/receivers', methods=['POST', 'GET'])
# def receivers():
#     if request.method=='POST':
#


# @app.route('/get-link', methods=['GET'])
# def get_link():
#     redirect_uri=request.get_json()['redirect_uri']
#
#     link = Flow.from_client_secrets_file(
#         'client_secret.json',
#         scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://mail.google.com/'],
#         redirect_uri=redirect_uri
#     ).\
#         authorization_url(access_type='offline',
#                           include_granted_scopes='true',
#                           prompt='consent')
#     return jsonify({'authorization_link': link[0]})

if __name__ == '__main__':
    app.run(debug=True)
# print(add_sender('123@123.com'))

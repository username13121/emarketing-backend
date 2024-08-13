from dotenv import load_dotenv
import os
import json

load_dotenv()

CLIENT_SECRET_FILE = 'config/client_secret.json'
with open(CLIENT_SECRET_FILE, 'r') as file:
    CLIENT_SECRET = json.load(file)

SCOPES = ['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://mail.google.com/']

SESSION_SECRET_KEY = os.getenv('SESSION_SECRET_KEY')

DB_NAME=os.getenv('DB_NAME')
DB_USER=os.getenv('DB_USER')
DB_PASSWORD=os.getenv('DB_PASSWORD')
DB_URL = 'postgresql://localhost:5432'


REDIS_URL='redis://localhost:6379'
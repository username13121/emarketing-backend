from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

from src.auth.crud import fetch_google_token, update_google_token

config = Config('.env')
oauth = OAuth(config)

oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email https://www.googleapis.com/auth/gmail.send'},

    authorize_params={
        'access_type': 'offline',
        'include_granted_scopes': 'true',
        'prompt': 'consent'
    },
    fetch_token=fetch_google_token,
    update_token=update_google_token
)
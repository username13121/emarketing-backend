from google.oauth2.credentials import Credentials
from google.oauth2 import id_token
from google.auth.transport.requests import Request as Oauth_request
from fastapi import HTTPException
from datetime import datetime



def get_missing_keys(dict: dict, keys: list) -> list:
    return [
        key 
        for key in keys
        if key not in dict
    ]

def creds_to_userdata(credentials: Credentials) -> dict:
    print(credentials.to_json())

    id_info = id_token.verify_oauth2_token(credentials.id_token, Oauth_request())
    userdata = {
        'email': id_info['email'],
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'id_token': credentials.id_token,
        'expiry': credentials.expiry.isoformat()
    }
    return userdata


def userdata_to_creds(userdata: dict,
                      client_secret: dict,
                      scopes: list[str]) -> Credentials:
    
    client_secret = client_secret.get('web', {})
    
    missing_keys = get_missing_keys(client_secret, ['token_uri', 'client_id', 'client_secret'])
    missing_keys.extend(get_missing_keys(userdata, ['token', 'refresh_token', 'id_token', 'expiry']))
    
    if missing_keys:
        raise ValueError(f'Missing some keys: {missing_keys}')
    
    credentials = Credentials(
        token=userdata.get('token'),
        refresh_token=userdata.get('refresh_token'),
        id_token=userdata.get('id_token'),
        expiry=datetime.fromisoformat(userdata.get('expiry')),

        token_uri=client_secret.get('token_uri'),
        client_id=client_secret.get('client_id'),
        client_secret=client_secret.get('client_secret'),
        scopes=scopes
    )


    return credentials
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from google_auth_oauthlib.flow import Flow
from pydantic import HttpUrl
from google.auth.transport.requests import Request as Oauth_request
from google.oauth2 import id_token
from google.auth.credentials import TokenState
from google.auth.exceptions import GoogleAuthError, RefreshError

import os
import logging

from tools import userdata_to_creds, creds_to_userdata
from config import CLIENT_SECRET, SCOPES, REDIS_URL
from middlewares import RedisSessionMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = FastAPI()

app.add_middleware(RedisSessionMiddleware, redis_url=REDIS_URL)

@app.exception_handler(GoogleAuthError)
async def google_auth_error_handler(request: Request, exc: GoogleAuthError):
    logger.error(f"GoogleAuthError: {exc}")
    return JSONResponse(status_code=401, content={"detail": "Unauthorized", "error": str(exc)})

@app.exception_handler(RefreshError)
async def refresh_error_handler(request: Request, exc: RefreshError):
    logger.error(f"RefreshError: {exc}")
    return JSONResponse(status_code=401, content={"detail": "Unauthorized", "error": str(exc)})

@app.get('/auth/url')
def get_auth_url(request: Request,
                  redirect_uri: HttpUrl):
    try:
        flow = Flow.from_client_config(CLIENT_SECRET,
                                   scopes=SCOPES,
                                   redirect_uri=redirect_uri)
        auth_url, _ = flow.authorization_url(access_type='offline',
                      include_granted_scopes='true',
                      prompt='consent')
        return {'auth_url': auth_url}
    
    except Exception as e:
        logger.error(f"Error generating auth link: {e}")
        raise HTTPException(status_code=500, detail="Error generating auth link")
    



@app.post('/auth/callback', status_code=201)
def auth_callback(request: Request, auth_response_url: HttpUrl):
    try:
        session = request.state.session

        auth_response_url = str(auth_response_url)
        redirect_uri = auth_response_url.split('?')[0]

    
        flow = Flow.from_client_config(CLIENT_SECRET, SCOPES, redirect_uri=redirect_uri)
        flow.fetch_token(authorization_response=auth_response_url)

        session = creds_to_userdata(flow.credentials)
    
        return {
        "message": "Success", 
        "user": {"email": session['email']}}
    
    except ValueError as e:
        logger.error(f"Invalid credentials: {e}")
        raise HTTPException(status_code=400, detail="Invalid credentials")
    except Exception as e:
        logger.error(f"Error processing callback: {e}")
        raise HTTPException(status_code=500, detail="Error processing callback")


@app.get('/auth/validate')
def auth_validate(request: Request):

    session = request.state.session

    if not session:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        credentials = userdata_to_creds(userdata=session,
                                    client_secret=CLIENT_SECRET,
                                    scopes=SCOPES)
    
        if credentials.token_state in {TokenState.STALE, TokenState.INVALID}:
            credentials.refresh(Oauth_request())
            session = creds_to_userdata(credentials)
    
        return {
            "message": "Success", 
            "user": {"email": session['email']}}
    except (GoogleAuthError, ValueError, KeyError) as e:
        logger.error(f"Unauthorized: {e}")
        raise HTTPException(status_code=401, detail="Unauthorized")
    except Exception as e:
        logger.error(f"Error validating auth: {e}")
        raise HTTPException(status_code=500, detail="Error validating auth")
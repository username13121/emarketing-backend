from authlib.integrations.starlette_client import OAuthError
from fastapi import APIRouter, Request, Depends
from fastapi.exceptions import HTTPException
from pydantic import HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from src.auth.crud import upsert_user_token
from src.auth.oauth2 import oauth
from src.database.dependencies import get_session
from .dependencies import get_user

auth_router = APIRouter(prefix='/auth', tags=['Authorization'])
google_oauth_router = APIRouter(prefix='/google')


@google_oauth_router.get('/login')
async def auth_google_login(request: Request, redirect_uri: HttpUrl = None):
    if redirect_uri is None:
        redirect_uri = request.url_for('auth_google_callback')

    return await oauth.google.authorize_redirect(request, redirect_uri)


@google_oauth_router.get('/callback')
async def auth_google_callback(request: Request, db_session: AsyncSession = Depends(get_session)):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as error:
        raise HTTPException(status_code=400, detail=error.description)
    user = await upsert_user_token(db_session, token, 'google')
    request.state.session = user.to_dict()
    return JSONResponse(request.state.session)


@google_oauth_router.get('/userdata')
async def auth_google_get_userdata(request: Request, user=Depends(get_user)):
    return user.to_dict()


# @google_oauth_router.post('/logout')
# async def auth_google_logout(request: Request, db_session: AsyncSession = Depends(get_session)):
#     print(await oauth.google.revoke(request=request))
#     await delete_token(db_session, request, 'google')
#     request.state.session = {}


auth_router.include_router(google_oauth_router)

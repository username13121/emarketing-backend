from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connection import AsyncSessionLocal
from src.models import UserModel
from src.schemas.user import Oauth2TokenSchema, Oauth2TokenUpdateSchema, UserSchema
from . import user_crud, oauth2_token_crud


async def fetch_google_token(request: Request):
    return (await oauth2_token_crud.read(AsyncSessionLocal(),
                                         user_id=int(request.state.session['id']),
                                         service_name='google')).scalar_one_or_none().to_token()


async def update_google_token(token, refresh_token=None, access_token=None):
    new_token = Oauth2TokenUpdateSchema(
        id_token=token['id_token'],
        access_token=token['access_token'],
        expires_at=token['expires_at']
    )
    if refresh_token:
        await oauth2_token_crud.update(
            AsyncSessionLocal(),
            new_token,
            refresh_token=refresh_token,
            service_name='google'
        )
    elif access_token:
        await oauth2_token_crud.update(
            AsyncSessionLocal(),
            new_token,
            access_token=access_token,
            service_name='google'
        )


async def upsert_user_token(db_session: AsyncSession, token: dict, oauth_service_name: str) -> UserModel:
    user_schema = UserSchema(email=token['userinfo']['email'])

    user_result = await user_crud.upsert(db_session,
                                         [user_schema],
                                         ['email'])

    user = user_result.scalar_one()

    token_schema = Oauth2TokenSchema(
        user_id=user.id,
        service_name=oauth_service_name,
        id_token=token['id_token'],
        access_token=token['access_token'],
        refresh_token=token['refresh_token'],
        expires_at=int(token['expires_at'])
    )
    token_result = await oauth2_token_crud.upsert(
        db_session,
        [token_schema],
        ['user_id', 'service_name'])
    token = token_result.scalar_one()
    print(user, token, '\n\n\n\n')

    return user
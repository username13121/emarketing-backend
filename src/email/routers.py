from fastapi import APIRouter, Depends, Request
from src.database.dependencies import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.oauth2 import oauth
from src.email.utils import create_message
from authlib.integrations.starlette_client import OAuthError
from fastapi.exceptions import HTTPException
from src.recipients.dependencies import get_recipients
from src.models import RecipientModel

email_router = APIRouter(prefix='/email', tags=['Email'])


@email_router.post('/gmail/send', status_code=201)
async def gmail_send(request: Request,
                     subject: str,
                     body: str,
                     subtype: str,
                     recipients: list[RecipientModel] = Depends(get_recipients),
                     db_session: AsyncSession = Depends(get_session)):

    if not recipients:
        raise HTTPException(400, 'No recipients')

    payload = {'raw': create_message(
        '',
        ', '.join(recipient.email for recipient in recipients),
        subject,
        body,
        subtype
    )}
    try:
        response = await oauth.google.post(
            'https://www.googleapis.com/gmail/v1/users/me/messages/send',
            json=payload,
            request=request
        )
    except OAuthError:
        raise HTTPException(status_code=401, detail='Unauthorized')

    return response.json()
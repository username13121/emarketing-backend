from fastapi import Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.dependencies import get_session
from .crud import user_crud


async def get_user_id(request: Request):
    user_id = request.state.session.get('id')
    if user_id is None:
        raise HTTPException(401, 'Unauthorized')
    return int(user_id)


async def get_user(request: Request, db_session: AsyncSession = Depends(get_session)):
    if request.state.session.get('id') is None:
        raise HTTPException(401, 'Unauthorized')

    user_id = int(request.state.session['id'])
    user = (await user_crud.read(db_session, id=user_id)).scalar_one_or_none()

    if user is None:
        request.state.session.pop('id')
        raise HTTPException(401, 'Unauthorized')

    return user

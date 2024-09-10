from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_user
from src.database.dependencies import get_session
from . import rec_list_crud
from src.models import UserModel


async def get_rec_list(
        rec_list_id: int,
        user: UserModel = Depends(get_user),
        db_session: AsyncSession = Depends(get_session)):
    rec_list = (await rec_list_crud.read(db_session,
                                         user_id=user.id,
                                         id=rec_list_id)).scalar_one_or_none()
    if rec_list is None:
        raise HTTPException(status_code=404, detail='Recipient list not found')

    return rec_list

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.dependencies import get_session
from src.models import RecListModel
from src.rec_lists.dependencies import get_rec_list
from . import recipients_crud


async def get_recipients(
        rec_list: RecListModel = Depends(get_rec_list),
        db_session: AsyncSession = Depends(get_session)):
    result = await recipients_crud.read(db_session, rec_list_id=rec_list.id)
    return result.scalars().all()
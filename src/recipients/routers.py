from fastapi import APIRouter, Request, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.dependencies import get_session
from src.models import RecListModel
from src.rec_lists.dependencies import get_rec_list
from src.schemas.recipients import RecipientCreateSchema
from . import recipients_crud

recipients_router = APIRouter(prefix='/rec_lists/{rec_list_id}/recipients', tags=['Recipients'])


@recipients_router.post('/', status_code=201)
async def create_recipient(request: Request,
                           recipient_schema: RecipientCreateSchema,
                           db_session: AsyncSession = Depends(get_session),
                           rec_list: RecListModel = Depends(get_rec_list)):
    try:
        result = await recipients_crud.create(db_session, [recipient_schema], rec_list_id=rec_list.id)
    except IntegrityError as error:
        raise HTTPException(400, error.__str__())
    return result.scalar_one()


@recipients_router.post('/bulk', status_code=201)
async def create_recipient_bulk(request: Request,
                                recipients_schema: list[RecipientCreateSchema],
                                db_session: AsyncSession = Depends(get_session),
                                rec_list: RecListModel = Depends(get_rec_list)):
    try:
        result = await recipients_crud.create(db_session, recipients_schema, rec_list_id=rec_list.id)
    except IntegrityError as error:
        raise HTTPException(400, error.__str__())
    return result.scalars().all()


@recipients_router.get('/')
async def get_all_recipients(request: Request,
                             db_session: AsyncSession = Depends(get_session),
                             rec_list: RecListModel = Depends(get_rec_list)):
    result = await recipients_crud.read(db_session, rec_list_id=rec_list.id)
    recipients = result.scalars().all()
    return recipients


@recipients_router.get('/{recipient_id}')
async def get_recipient(
        recipient_id: int,
        request: Request,
        db_session: AsyncSession = Depends(get_session),
        rec_list: RecListModel = Depends(get_rec_list)):
    result = await recipients_crud.read(db_session, rec_list_id=rec_list.id, id=recipient_id)
    recipient = result.scalar_one_or_none()

    if recipient is None:
        raise HTTPException(404, 'Recipient not found in the list')
    return recipient


@recipients_router.put('/{recipient_id}')
async def put_recipient(
        recipient_schema: RecipientCreateSchema,
        recipient_id: int,
        request: Request,
        db_session: AsyncSession = Depends(get_session),
        rec_list: RecListModel = Depends(get_rec_list)):
    try:
        result = await recipients_crud.update(db_session,
                                              recipient_schema,
                                              id=recipient_id,
                                              rec_list_id=rec_list.id
                                              )
    except IntegrityError as error:
        raise HTTPException(400, error.__str__())
    recipient = result.scalar_one_or_none()
    if recipient is None:
        raise HTTPException(404, 'Recipient not found in the list')

    return recipient


@recipients_router.delete('/{recipient_id}')
async def delete_recipient(
        recipient_id: int,
        request: Request,
        db_session: AsyncSession = Depends(get_session),
        rec_list: RecListModel = Depends(get_rec_list)):
    result = await recipients_crud.delete(db_session, id=recipient_id, rec_list_id=rec_list.id)
    recipient = result.scalar_one_or_none()

    if recipient is None:
        raise HTTPException(404, 'Recipient not found in the list')

    return recipient


@recipients_router.delete('/')
async def delete_all_recipients(
        request: Request,
        db_session: AsyncSession = Depends(get_session),
        rec_list: RecListModel = Depends(get_rec_list)):
    result = await recipients_crud.delete(db_session, rec_list_id=rec_list.id)
    recipients = result.scalars().all()

    return recipients

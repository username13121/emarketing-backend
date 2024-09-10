from fastapi import APIRouter, Request, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_user
from src.database.dependencies import get_session
from src.models import RecListModel, UserModel
from src.schemas.recipients import RecListCreateSchema
from . import rec_list_crud

rec_lists_router = APIRouter(prefix='/rec_lists', tags=['Recipient lists'])


@rec_lists_router.post('/')
async def create_rec_list(rec_list_schema: RecListCreateSchema,
                          request: Request,
                          db_session: AsyncSession = Depends(get_session),
                          user: UserModel = Depends(get_user)):
    try:
        result = await rec_list_crud.create(db_session, [rec_list_schema], user_id=user.id)
    except IntegrityError as error:
        raise HTTPException(400, error.__str__())

    return result.scalar_one()


@rec_lists_router.get('/')
async def get_rec_lists(request: Request,
                        db_session: AsyncSession = Depends(get_session),
                        user: UserModel = Depends(get_user)):
    result = await rec_list_crud.read(db_session,
                                      [RecListModel.recipients],
                                      user_id=user.id)
    rec_lists = result.unique().scalars().all()

    return rec_lists


@rec_lists_router.get('/{rec_list_id}')
async def get_rec_lists(rec_list_id: int,
                        request: Request,
                        db_session: AsyncSession = Depends(get_session),
                        user: UserModel = Depends(get_user)):
    result = await rec_list_crud.read(db_session,
                                      [RecListModel.recipients],
                                      id=rec_list_id,
                                      user_id=user.id)

    rec_list = result.unique().scalar_one_or_none()

    if rec_list is None:
        raise HTTPException(404, 'Not found')

    return rec_list


@rec_lists_router.put('/{rec_list_id}')
async def put_rec_list(rec_list_id: int,
                       rec_list_schema: RecListCreateSchema, request: Request,
                       db_session: AsyncSession = Depends(get_session),
                       user: UserModel = Depends(get_user)):
    try:
        result = await rec_list_crud.update(db_session,
                                            rec_list_schema,
                                            user_id=user.id,
                                            id=rec_list_id)
    except IntegrityError as error:
        raise HTTPException(400, error.__str__())

    rec_list = result.unique().scalar_one_or_none()

    if rec_list is None:
        raise HTTPException(404, 'Recipient list not found')

    return rec_list


@rec_lists_router.delete('/{rec_list_id}')
async def delete_rec_list(rec_list_id: int,
                          request: Request,
                          db_session: AsyncSession = Depends(get_session),
                          user: UserModel = Depends(get_user)):
    result = await rec_list_crud.delete(db_session, id=rec_list_id, user_id=user.id)
    rec_list = result.scalar_one_or_none()

    if rec_list is None:
        raise HTTPException(404, 'Recipient list not found')

    return rec_list

from sqlalchemy.orm import declarative_base, joinedload as sqlalchemy_joined_load
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select, update, delete
from pydantic import BaseModel
from typing import Type
from sqlalchemy.ext.asyncio import AsyncSession

Base = declarative_base()


class CRUDHandler:
    def __init__(self, model: Type[Base]):
        self.model = model
        self.columns = [c.name for c in self.model.__table__.columns]

    async def create(self, db_session: AsyncSession, entities: list[BaseModel], **kwargs):
        return await self.execute(
            db_session,
            self._create_stmt(entities, **kwargs))

    async def read(self, db_session: AsyncSession, joined_load: list = None, **filters_kwargs):
        return await self.execute(
            db_session,
            self._read_stmt(joined_load, **filters_kwargs))

    async def update(self, db_session: AsyncSession, schema: BaseModel, **filters_kwargs):
        return await self.execute(
            db_session,
            self._update_stmt(schema, **filters_kwargs))

    async def upsert(self, db_session: AsyncSession, schemas: list[BaseModel], index_elements: list[str], **kwargs):
        return await self.execute(
            db_session,
            self._upsert_stmt(schemas, index_elements, **kwargs)
        )

    async def delete(self, db_session: AsyncSession, **filter_kwargs):
        return await self.execute(
            db_session,
            self._delete_stmt(**filter_kwargs))

    def _create_stmt(self, entities: list[BaseModel], **kwargs):
        data_to_insert = [{**entity.dict(), **kwargs} for entity in entities]

        return insert(self.model).values(data_to_insert).returning(self.model)

    def _read_stmt(self, joined_load: list = None, **filters_kwargs):
        stmt = select(self.model).filter_by(**filters_kwargs)
        if joined_load is not None:
            stmt = stmt.options(sqlalchemy_joined_load(*joined_load))
        return stmt

    def _update_stmt(self, schema: BaseModel, **filters_kwargs):
        return update(self.model).filter_by(**filters_kwargs).values(**schema.dict()).returning(self.model)

    def _upsert_stmt(self, schemas: list[BaseModel], index_elements: list[str], **kwargs):
        values = [{**schema.dict(), **kwargs} for schema in schemas]

        stmt = insert(self.model).values(values)
        set_dict = {col: stmt.excluded[col] for col in self.columns if col not in ['id']}

        return stmt.on_conflict_do_update(
                index_elements=index_elements,
                set_=set_dict
            ).returning(self.model)

    def _delete_stmt(self, **filters_kwargs):
        return delete(self.model).filter_by(**filters_kwargs).returning(self.model)

    @staticmethod
    async def execute(db_session: AsyncSession, statement):
        async with db_session.begin():
            return await db_session.execute(statement)

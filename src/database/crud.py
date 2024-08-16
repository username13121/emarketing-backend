from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from src.config import settings
from src.database.models import Base, User, RecList, Recipient
from collections import defaultdict

from src.database import create_tables, get_session
from sqlalchemy.future import select
from sqlalchemy import join, and_, insert, update, delete
from sqlalchemy import Select, Subquery
from sqlalchemy.dialects.postgresql import insert as postgres_insert


def fetch_user(user_email: str,
               return_columns: list[User] = (User,)) -> Select:
    return select(*return_columns).filter(User.email == user_email)


def fetch_rec_lists(fetched_user: Select | Subquery,
                    rec_list_name: str = None,
                    return_columns: list[RecList] = (RecList,)) -> Select:
    return (
        select(*return_columns).filter(
            and_(
                RecList.user_id == fetched_user.c.id,
                *(RecList.name == rec_list_name,) if rec_list_name is not None else ()
            )))


def fetch_recs(fetched_lists: Select | Subquery,
               return_columns: list[Recipient] = (Recipient,)) -> Select:
    return (
        select(*return_columns).filter(
            Recipient.rec_list_id == fetched_lists.c.id
        )
    )

async def create_user(db_session: AsyncSession, user_email: str):
    async with db_session.begin():
        stmt = (
            postgres_insert(User)
            .values(email=user_email)
            .on_conflict_do_nothing(index_elements=['email'])
        )
        await db_session.execute(stmt)


async def get_rec_lists(db_session: AsyncSession, user_email: str, rec_list_name: str = None):
    # Define the SQLAlchemy query
    async with db_session.begin():

        fetched_rec_lists = fetch_rec_lists(
            fetched_user=fetch_user(user_email),
            rec_list_name=rec_list_name
        ).subquery()

        fetched_recs = fetch_recs(
            fetched_lists=fetched_rec_lists).subquery()

        # Join subqueries
        stmt = (
            select(fetched_rec_lists.c.name, fetched_recs.c.email).select_from(
                fetched_rec_lists.join(
                    fetched_recs,
                    fetched_rec_lists.c.id == fetched_recs.c.rec_list_id,
                    isouter=True
                )
            )
        )

        join_result = await db_session.execute(stmt)
        result_dict = defaultdict(list)

        for rec_list_name, recipient_email in join_result:
            if recipient_email is None:
                result_dict[rec_list_name] = []
                continue

            result_dict[rec_list_name].append(recipient_email)

        return result_dict


# Note: optimize this
async def create_populate_rec_list(db_session: AsyncSession, user_email: str, rec_list_name: str,
                                   rec_emails: list[str] = None):
    async with db_session.begin():
        rec_list_stmt = insert(RecList).values(user_id=fetch_user(user_email=user_email,
                                                                  return_columns=[User.id]
                                                                  ).scalar_subquery(),
                                               name=rec_list_name
                                               ).returning(RecList.id, RecList.name)

        rec_list = (await db_session.execute(rec_list_stmt)).mappings().fetchone()

        if rec_emails is None:
            return {rec_list['name']: []}

        rec_stmt = insert(Recipient).values([
            {'rec_list_id': rec_list['id'], 'email': email}
            for email in rec_emails
        ])

        result = await db_session.execute(rec_stmt.returning(Recipient.email))
        result_dict = {rec_list['name']: [res for res in result.scalars()]}
        return result_dict


# Note: optimize this
async def rename_rec_list(db_session: AsyncSession, user_email: str, rec_list_name: str, new_rec_list_name: str):
    async with db_session.begin():
        stmt = update(RecList).filter(

            RecList.id == fetch_rec_lists(
                fetched_user=fetch_user(user_email=user_email),

                rec_list_name=rec_list_name,
                return_columns=[RecList.id]
            )
        ). \
            values(name=new_rec_list_name). \
            returning(RecList.name)

        fetched_new_rec_list_name = await db_session.execute(stmt)

        return fetched_new_rec_list_name.mappings().fetchone()


async def add_recs_to_list(db_session: AsyncSession, user_email: str, rec_list_name: str, recipients: list[str]):
    async with db_session.begin():
        fetched_rec_list = fetch_rec_lists(
            fetched_user=fetch_user(user_email=user_email, return_columns=[User.id]),
            rec_list_name=rec_list_name,

            return_columns=[RecList.id]
        ).scalar_subquery()

        stmt = insert(Recipient).values([
            {'rec_list_id': fetched_rec_list, 'email': rec_email}
            for rec_email in recipients
        ]).returning(Recipient.email)

        returned_recs = await db_session.execute(stmt)
        result = {
            rec_list_name: returned_recs.scalars().all()
        }
        return result


async def delete_lists(db_session: AsyncSession, user_email: str, rec_list_names: str = None):
    async with db_session.begin():
        stmt = delete(RecList).filter(
            and_(
                RecList.id == fetch_rec_lists(fetched_user=fetch_user(user_email),
                                              return_columns=[RecList.id]
                                              ).scalar_subquery(),
                (RecList.name == rec_list_names if rec_list_names else True)
            )
        ).returning(RecList.name)

        deleted_rec_list_names = await db_session.execute(stmt)
        return deleted_rec_list_names.scalars().all()

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from src.config import settings
from src.database.models import Base, User, RecList, Recipient
from collections import defaultdict

from src.database import create_tables, get_session
from sqlalchemy.future import select
from sqlalchemy import join, and_, insert


# async def get_rec_lists(db_session: AsyncSession, email: str, rec_list_name: str = None) -> list:
#     async with db_session:
#         async with db_session.begin():
#             stmt = select(Recipient).join(
#                 RecList,
#                 (Recipient.rec_list_id == RecList.id) &
#                 (Recipient.rec_list_user_id == RecList.user_id)
#             ).where(
#                 Recipient.email == email
#             )
#             if rec_list_name is not None:
#                 stmt = stmt.where(RecList.name == rec_list_name)
#
#             results = await db_session.execute(stmt)
#             return results.scalar().all()


async def get_rec_lists(db_session: AsyncSession, email: str, rec_list_name: str = None):
    # Define the SQLAlchemy query
    async with db_session.begin():
        # Get user by email
        filtered_users = select(User).filter(User.email == email)

        # Subquery for filtered rec_lists
        filtered_rec_lists = (
            select(RecList.id, RecList.name, RecList.user_id)
            .filter(RecList.user_id.in_(select(filtered_users.c.id)))
        )

        # Find specific list if specified
        if rec_list_name is not None:
            filtered_rec_lists = filtered_rec_lists.filter(RecList.name == rec_list_name)

        filtered_rec_lists = filtered_rec_lists.subquery()

        # Subquery for filtered recipients
        filtered_recs = (
            select(Recipient.email, Recipient.rec_list_id, Recipient.rec_list_user_id)
            .filter(Recipient.rec_list_user_id.in_(select(filtered_users.c.id)))
            .subquery()
        )

        # Join subqueries
        stmt = (
            select(filtered_rec_lists.c.name, filtered_recs.c.email)
            .select_from(
                filtered_rec_lists.join(
                    filtered_recs,
                    and_(
                        filtered_rec_lists.c.id == filtered_recs.c.rec_list_id,
                        filtered_rec_lists.c.user_id == filtered_recs.c.rec_list_user_id
                    )
                )
            )
        )

        join_result = await db_session.execute(stmt)
        result_dict = defaultdict(list)

        for rec_list_name, recipient_email in join_result:
            result_dict[rec_list_name].append(recipient_email)

        return result_dict


async def create_populate_rec_list(db_session: AsyncSession, user_email: str, rec_list_name: str, rec_emails: list[str]):
    async with db_session.begin():
        user = select(User.id).filter(User.email == user_email).scalar_subquery()

        rec_list = (await db_session.execute(
            insert(RecList).values(user_id=user, name=rec_list_name)
            .returning(RecList.id, RecList.user_id)
        )).scalar()

        print(rec_list)

        stmt = insert(Recipient).values([
            {'email': email, 'rec_list_id': rec_list['id'], 'rec_list_user_id': rec_list['user_id']}
            for email in rec_emails
        ])

        return await db_session.execute(stmt.returning())

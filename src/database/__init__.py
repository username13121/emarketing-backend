from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from src.config import settings
from src.database.models import Base, User, RecList, Recipient

async_engine = create_async_engine(settings.DATABASE_URL_asyncpg,
                                   echo=True
                                   )

AsyncSessionLocal = sessionmaker(bind=async_engine,
                                 class_=AsyncSession,
                                 expire_on_commit=False)


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as db_session:
        yield db_session


async def create_tables():
    async with async_engine.connect() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.commit()


async def populate_tables():
    async with AsyncSessionLocal() as db_session:
        user1 = User(email='username12312355@gmail.com')
        user2 = User(email='user2@mail.ru')
        user3 = User(email='user3@gmail.com')
        db_session.add(user1)
        db_session.add(user2)
        db_session.add(user3)

        await db_session.commit()

        rec_list1 = RecList(user_id=user1.id, name='user1_list1')
        rec_list2 = RecList(user_id=user1.id, name='user1_list2')
        rec_list3 = RecList(user_id=user2.id, name='user2_list1')
        rec_list4 = RecList(user_id=user3.id, name='user3_list1')

        db_session.add(rec_list1)
        db_session.add(rec_list2)
        db_session.add(rec_list3)
        db_session.add(rec_list4)
        await db_session.commit()

        recipient1 = Recipient(email='user1_list1@example.com', rec_list_id=rec_list1.id)
        recipient2 = Recipient(email='user1_list1@gmail.com', rec_list_id=rec_list1.id)
        recipient3 = Recipient(email='user1_list2@gmail.com', rec_list_id=rec_list2.id)
        recipient4 = Recipient(email='user2_list1@example.com', rec_list_id=rec_list3.id)
        recipient5 = Recipient(email='user3_list1@example.com', rec_list_id=rec_list4.id)

        db_session.add(recipient1)
        db_session.add(recipient2)
        db_session.add(recipient3)
        db_session.add(recipient4)
        db_session.add(recipient5)

        await db_session.commit()

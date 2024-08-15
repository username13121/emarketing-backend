from sqlalchemy import Table, Column, Integer, String, ForeignKey, UniqueConstraint, PrimaryKeyConstraint, Text, \
    ForeignKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, unique=True)


class RecList(Base):
    __tablename__ = 'rec_lists'

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    id: Mapped[int] = mapped_column(nullable=False, primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)

    __table_args__ = ( # Note: get rid of composite primary key
        PrimaryKeyConstraint('user_id', 'id'),
        UniqueConstraint('user_id', 'id', 'name')
    )


class Recipient(Base):
    __tablename__ = 'recipients'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(nullable=False)

    rec_list_id: Mapped[int] = mapped_column(nullable=False)
    rec_list_user_id: Mapped[int] = mapped_column(nullable=False)

    __table_args__ = (
        UniqueConstraint('rec_list_user_id', 'rec_list_id', 'email'),
        ForeignKeyConstraint(
            ['rec_list_id', 'rec_list_user_id'],
            ['rec_lists.id', 'rec_lists.user_id'],
            ondelete='CASCADE'
        )
    )
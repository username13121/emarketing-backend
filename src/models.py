from sqlalchemy import Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship

Base = declarative_base()


class UserModel(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    tokens = relationship('Oauth2TokenModel', back_populates='user')
    rec_lists = relationship('RecListModel', back_populates='user')

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email
        }


class Oauth2TokenModel(Base):
    __tablename__ = 'tokens'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    service_name: Mapped[str] = mapped_column(String, nullable=False)
    id_token: Mapped[str] = mapped_column(String, nullable=False)
    access_token: Mapped[str] = mapped_column(String, nullable=False)
    refresh_token: Mapped[str] = mapped_column(String, nullable=False)
    expires_at: Mapped[int] = mapped_column(Integer, nullable=False)

    user: Mapped[UserModel] = relationship('UserModel', back_populates='tokens')

    __table_args__ = (
        UniqueConstraint('service_name', 'user_id'),
    )

    def to_token(self):
        return {
            'id_token': self.id_token,
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'expires_at': self.expires_at
        }


class RecListModel(Base):
    __tablename__ = 'rec_lists'

    id: Mapped[int] = mapped_column(nullable=False, primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    user: Mapped[UserModel] = relationship('UserModel', back_populates='rec_lists')

    recipients = relationship('RecipientModel', back_populates='rec_list')

    __table_args__ = (
        UniqueConstraint('user_id', 'name'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name
        }


class RecipientModel(Base):
    __tablename__ = 'recipients'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(nullable=False)

    rec_list_id: Mapped[int] = mapped_column(ForeignKey('rec_lists.id', ondelete='CASCADE'), nullable=False)
    rec_list: Mapped[RecListModel] = relationship('RecListModel', back_populates='recipients')

    __table_args__ = (
        UniqueConstraint('rec_list_id', 'email'),
    )

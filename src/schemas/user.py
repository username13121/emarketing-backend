from pydantic import BaseModel, EmailStr
from typing import Optional


class UserSchema(BaseModel):
    email: EmailStr


class UserUpdateSchema(UserSchema):
    id: int


class Oauth2TokenSchema(BaseModel):
    user_id: int
    service_name: str
    id_token: str
    access_token: str
    refresh_token: str
    expires_at: int


class Oauth2TokenUpdateSchema(BaseModel):
    id_token: str
    access_token: str
    expires_at: int

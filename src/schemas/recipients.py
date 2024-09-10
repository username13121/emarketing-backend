from pydantic import BaseModel, EmailStr
from typing import Optional


class RecListCreateSchema(BaseModel):
    name: str


class RecListFullSchema(RecListCreateSchema):
    user_id: int


class RecipientCreateSchema(BaseModel):
    email: EmailStr


class RecipientFullSchema(RecipientCreateSchema):
    rec_list_id: int


class RecipientUpdateSchema(BaseModel):
    rec_list_id: int
    email: Optional[EmailStr]
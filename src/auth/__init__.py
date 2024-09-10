from src.crud_handler import CRUDHandler
from src.models import UserModel, Oauth2TokenModel


user_crud = CRUDHandler(UserModel)
oauth2_token_crud = CRUDHandler(Oauth2TokenModel)
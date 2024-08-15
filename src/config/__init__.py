from pydantic_settings import BaseSettings, SettingsConfigDict

from dotenv import load_dotenv
import os
import json

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CLIENT_SECRET_FILE = os.path.join(BASE_DIR, 'client_secret.json')
with open(CLIENT_SECRET_FILE, 'r') as file:
    CLIENT_SECRET = json.load(file)

SCOPES = ['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://mail.google.com/']

REDIS_URL = 'redis://localhost:6379'


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def DATABASE_URL_asyncpg(self):
        # postgresql+asyncpg://postgres:postgres@localhost:5432/sa
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()

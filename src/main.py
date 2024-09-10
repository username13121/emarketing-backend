from fastapi import FastAPI
from src.auth.routers import auth_router
from starlette.middleware import Middleware
from src.middlewares import RedisSessionMiddleware
from starlette.middleware.sessions import SessionMiddleware

from src.database.connection import create_tables
from src.email.routers import email_router
from src.rec_lists.routers import rec_lists_router
from src.recipients.routers import recipients_router
from src.config import settings


app = FastAPI(
    middleware=[
        Middleware(SessionMiddleware, secret_key="secret_key13121"),
        Middleware(RedisSessionMiddleware, redis_url=settings.REDIS_URL)
    ]
)
app.include_router(auth_router)
app.include_router(email_router)
app.include_router(rec_lists_router)
app.include_router(recipients_router)


@app.on_event('startup')
async def on_startup():
    await create_tables()

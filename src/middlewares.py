import uuid

import redis
from fastapi import Request
from pydantic import HttpUrl
from starlette.middleware.base import BaseHTTPMiddleware


class RedisSessionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis_url: HttpUrl):
        super().__init__(app)
        self.redis = redis.asyncio.from_url(redis_url, decode_responses=True)

    async def dispatch(self, request: Request, call_next):

        # Validate session_id in cookies
        try:
            uuid.UUID(hex=request.cookies.get('session_id'), version=4)
            session_id = request.cookies.get('session_id')
        # If invalid, generate new session_id
        except (ValueError, TypeError):
            session_id = str(uuid.uuid4())

        # Get session data from Redis
        request.state.session = await self.redis.hgetall(session_id)

        # Save pre request session data
        session_data_pre = request.state.session.copy()
        # Run the route
        response = await call_next(request)

        session_data_post = request.state.session
        # Check for new or updated keys
        updates = {
            key: value
            for key, value in session_data_post.items()
            if value != session_data_pre.get(key)
        }

        # Check for deleted keys
        deletes = [
            key
            for key in session_data_pre
            if key not in session_data_post
        ]

        # If keys were updated/deleted, update/delete them in redis
        if updates:
            await self.redis.hset(session_id, mapping=updates)
        if deletes:
            await self.redis.hdel(session_id, *deletes)

        # If new session_id was generated, set it
        if request.cookies.get('session_id') != session_id:
            response.set_cookie('session_id', session_id)

        return response

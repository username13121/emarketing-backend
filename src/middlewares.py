import redis
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
import starlette.exceptions

import uuid


class RedisSessionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis_url: str):
        super().__init__(app)
        self.redis = redis.asyncio.from_url(redis_url, decode_responses=True)

    async def dispatch(self, request: Request, call_next):

        # Get session id from cookies or generate new one
        session_id = request.cookies.get('session_id',
                                         str(uuid.uuid4()))

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

        # If session_id isn't in cookies, write it
        if request.cookies.get('session_id') is None:
            response.set_cookie('session_id', session_id)

        return response

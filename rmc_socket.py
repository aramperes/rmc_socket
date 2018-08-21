import asyncio
from threading import Thread

import redis
import socketio
from aiohttp import web
from redis import Redis

VOTECOUNT_NAMESPACE = "/voteCount"


class RMCSocketServer:

    def __init__(self, redis_host="127.0.0.1", redis_port=6379):
        self.redis_pool = redis.ConnectionPool(host=redis_host, port=redis_port, db=0)

        self.sio = socketio.AsyncServer(ping_interval=2)
        self.web = web.Application()
        self.sio.attach(self.web)
        self.active = True
        self.total = 0

        redis_loop = asyncio.new_event_loop()
        thread = Thread(target=self._parallel_redis, args=(redis_loop,))
        thread.start()

    def _parallel_redis(self, loop):
        loop.run_until_complete(self._redis_listen())

    async def _redis_listen(self):
        while self.active:
            r: Redis = self.redis()
            color_keys = r.keys("rmc:count:*")
            counts = r.mget(color_keys)
            self.total = sum(int(c) for c in counts)

            @self.sio.on("connect", namespace=VOTECOUNT_NAMESPACE)
            async def connect(sid, _):
                await self.sio.send(str(self.total), namespace=VOTECOUNT_NAMESPACE, room=sid)

            pubsub = r.pubsub()
            pubsub.subscribe("rmc:vote")
            while True:
                data = next(pubsub.listen())
                if data["type"] == "message" and data["channel"].decode() == "rmc:vote":
                    self.total += 1
                    await self.sio.send(str(self.total), namespace=VOTECOUNT_NAMESPACE)

    def redis(self):
        return redis.Redis(connection_pool=self.redis_pool)

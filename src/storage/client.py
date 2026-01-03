import json

from redis.asyncio import Redis
from redis.typing import KeyT, FieldT


class AsyncRedisOverride:
    def __init__(
        self,
        host: str,
        port: int,
        password: str = None,
        db: int = 0
    ):
        self.__redis = Redis(
            host=host,
            port=port,
            password=password,
            decode_responses=True,
            db=db
        )

    async def delete(self, *names: bytes | str | memoryview):
        await self.__redis.delete(*names)

    async def hset(
        self,
        name: str,
        key: str | None = None,
        value: str | None = None,
        mapping: dict | None = None,
        items: list | None = None
    ):
        if type(value) is not str:
            value = json.dumps(value)
        return await self.__redis.hset(name, key, value, mapping, items)

    async def hgetall(self, name: str):
        return await self.__redis.hgetall(name)

    async def sadd(self, name: KeyT, *values: FieldT):
        return await self.__redis.sadd(name, *values)

    async def smembers(self, name: KeyT):
        return await self.__redis.smembers(name)

    async def srem(self, name: KeyT, *values: FieldT):
        return await self.__redis.srem(name, *values)

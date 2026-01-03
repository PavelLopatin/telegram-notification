import contextlib
import json
from typing import Any, Union

from redis.asyncio import Redis
from redis.typing import ExpiryT, KeyT, KeysT, PatternT, FieldT


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

    async def set(
        self,
        key: str,
        value: Union[str, dict, list, int],
        ex: int = None,
    ):
        if type(value) is not str:
            value = json.dumps(value)
        await self.__redis.set(key, value, ex=ex)

    async def get(self, key: str, default=None) -> Any:
        value = await self.__redis.get(key)
        if value is None:
            return default

        with contextlib.suppress(Exception):
            value = json.loads(value)
        return value

    async def close(self):
        await self.__redis.aclose()

    async def exist(self, *names: str) -> bool:
        return bool(await self.__redis.exists(*names))

    async def mset(self, data: dict):
        await self.__redis.mset(data)

    async def delete(self, *names: bytes | str | memoryview):
        await self.__redis.delete(*names)

    async def lpush(self, name: str, *values: bytes | memoryview | str | int | float):
        await self.__redis.lpush(name, *values)

    async def lrem(self, name: str, value: str, count: int = 0):
        await self.__redis.lrem(name, count, value)

    async def lrange(self, name: str, start: int = 0, end: int = -1):
        return await self.__redis.lrange(name, start, end)

    async def llen(self, name: str):
        return await self.__redis.llen(name)

    async def keys(self, pattern: str):
        return await self.__redis.keys(pattern)

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

    async def hexpire(
        self,
        name: KeyT,
        seconds: ExpiryT,
        *fields: str,
        nx: bool = False,
        xx: bool = False,
        gt: bool = False,
        lt: bool = False,
    ):
        return await self.__redis.hexpire(name, seconds, *fields, nx=nx, xx=xx, gt=gt, lt=lt)

    async def hgetall(self, name: str):
        return await self.__redis.hgetall(name)

    async def hmget(self, name: str, keys: list[str]):
        return await self.__redis.hmget(name, keys)

    async def hexists(self, name: str, key: str):
        return await self.__redis.hexists(name, key)

    async def hkeys(self, name: str):
        return await self.__redis.hkeys(name)

    async def hdel(self, name: str, *keys: str):
        return await self.__redis.hdel(name, *keys)

    async def hget(self, name: str, key: str, default: Any = None):
        result = await self.__redis.hget(name, key)
        if result is None:
            return default
        return result

    async def mget(self, *keys: KeysT):
        return await self.__redis.mget(keys)

    async def hscan(
        self,
        name: KeyT,
        cursor: int = 0,
        match: Union[PatternT, None] = None,
        count: Union[int, None] = None,
        no_values: Union[bool, None] = None,
    ):
        return await self.__redis.hscan(name, cursor, match, count, no_values)

    async def scan(
        self,
        cursor: int = 0,
        match: Union[PatternT, None] = None,
        count: Union[int, None] = None,
        _type: Union[str, None] = None,
        **kwargs,
    ):
        return await self.__redis.scan(cursor, match, count, _type, **kwargs)

    async def sadd(self, name: KeyT, *values: FieldT):
        return await self.__redis.sadd(name, *values)

    async def smembers(self, name: KeyT):
        return await self.__redis.smembers(name)

    async def srem(self, name: KeyT, *values: FieldT):
        return await self.__redis.srem(name, *values)

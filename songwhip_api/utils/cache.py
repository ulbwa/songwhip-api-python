import asyncio

from cachetools.func import lru_cache, ttl_cache  # pip: cachetools
from cache import AsyncLRU, AsyncTTL  # pip: async-cache


class TTLCache:
    def __init__(self, time_to_live: int, maxsize: int):
        self.time_to_live = time_to_live
        self.maxsize = maxsize
        self.__obj = None

    def __call__(self, func):
        def set_obj():
            if asyncio.iscoroutinefunction(func):
                self.__obj = AsyncTTL(
                    time_to_live=self.time_to_live, maxsize=self.maxsize
                )
            else:
                self.__obj = ttl_cache(ttl=self.time_to_live, maxsize=self.maxsize)

        def sync_wrapper(*args, use_cache: bool = True, **kwargs):
            if self.__obj is None or not use_cache:
                set_obj()
            return self.__obj(func)(*args, **kwargs)

        async def async_wrapper(*args, use_cache: bool = True, **kwargs):
            if self.__obj is None or not use_cache:
                set_obj()
            return await self.__obj(func)(*args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            sync_wrapper.__name__ += func.__name__
            return sync_wrapper


class LRUCache:
    def __init__(self, maxsize: int):
        self.maxsize = maxsize
        self.__obj = None

    def __call__(self, func):
        def set_obj():
            if asyncio.iscoroutinefunction(func):
                self.__obj = AsyncLRU(maxsize=self.maxsize)
            else:
                self.__obj = lru_cache(maxsize=self.maxsize)

        def sync_wrapper(*args, use_cache: bool = True, **kwargs):
            if self.__obj is None or not use_cache:
                set_obj()
            return self.__obj(func)(*args, **kwargs)

        async def async_wrapper(*args, use_cache: bool = True, **kwargs):
            if self.__obj is None or not use_cache:
                set_obj()
            return await self.__obj(func)(*args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            sync_wrapper.__name__ += func.__name__
            return sync_wrapper

import logging
import random
import urllib.parse
import urllib.parse
from datetime import timedelta
from typing import List, Union, Optional

import orjson
from aiohttp_client_cache import CachedSession, FileBackend, CacheBackend
from aiohttp_proxy import ProxyConnector
from fake_headers import Headers

logger = logging.getLogger("songwhip_api")

from songwhip_api.types import *


class SongWhip:
    """
    Class for interacting with the SongWhip API.
    """

    api_url: str
    api_timeout: int
    always_use_proxy: bool
    cache_backend: Optional[CacheBackend]

    __connections: List[Optional[str]]

    def __init__(
        self,
        api_url: str = "https://songwhip.com/",
        api_timeout: int = 60,
        proxy: Optional[Union[List[str], str]] = None,
        always_use_proxy: bool = False,
        cache_backend: Optional[CacheBackend] = FileBackend(
            expire_after=timedelta(days=31),
            ignored_parameters=["key"],
            allowed_codes=(200,),
            allowed_methods=["GET", "POST"],
            cache_control=False,
            use_temp=True,
        ),
    ):
        """
        Initialize the SongWhip instance.

        :param api_url: The base URL of the SongWhip API.
        :param api_timeout: Timeout for API requests in seconds.
        :param proxy: Proxy(s) to use for requests.
        :param always_use_proxy: Flag indicating whether to always use the provided proxy.
        :param cache_backend: Cache backend to use for caching API responses.
        """
        self.api_url = api_url.rstrip("/")
        self.api_timeout = api_timeout
        self.always_use_proxy = always_use_proxy
        self.cache_backend = cache_backend

        self.__connections = []
        if proxy is not None:
            for _proxy in proxy if isinstance(proxy, list) else [proxy]:
                self.__connections.append(_proxy)
        if not always_use_proxy:
            self.__connections.append(None)
        if not self.__connections:
            raise ValueError("No connections specified.")

    def __repr__(self) -> str:
        """
        Return the string representation of the SongWhip instance.

        :return: String representation of the SongWhip instance.
        """
        return f"<SongWhip at {hex(id(self))}>"

    async def request(self, url: str) -> Album | Track | Artist:
        """
        Make a request to the SongWhip API and return the corresponding entity.

        :param url: The URL of the song or album.

        :return: An instance of Album, Track, or Artist.
        """

        connection = random.choice(self.__connections)

        async with CachedSession(
            connector=ProxyConnector.from_url(connection) if connection else None,
            cache=self.cache_backend,
        ) as session:
            async with session.post(
                url=f"{self.api_url}/api/songwhip/create",
                headers={
                    **Headers(os="windows", headers=True).generate(),
                    "Content-Type": "application/json",
                    "Referer": f"{self.api_url}/convert?url={urllib.parse.quote(url)}&sourceAction=pasteUrl",
                },
                data=orjson.dumps({"url": url, "country": "US"}),
                timeout=self.api_timeout,
            ) as response:
                try:
                    raw_data = orjson.loads(await response.read())
                    logger.debug("Got response on URL %s: %s", response.url, raw_data)
                    data = raw_data["data"]["item"]
                except Exception as exception:
                    raise APIException(
                        status_code=response.status, message=str(exception)
                    ).with_traceback(exception.__traceback__)

            if response.status != 200 or data == {}:
                raise APIException(
                    status_code=response.status,
                    message=data.get("status", str(response.status)),
                )

            match EntityType(data["type"]):
                case EntityType.TRACK:
                    return Track.from_dict(data)
                case EntityType.ARTIST:
                    return Artist.from_dict(data)
                case EntityType.ALBUM:
                    return Album.from_dict(data)
                case entity_type:
                    raise APIException(
                        status_code=404,
                        message=f"Received unexpected value: {entity_type=}",
                    )

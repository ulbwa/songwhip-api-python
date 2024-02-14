import logging
import random
import urllib.parse
import urllib.parse
from datetime import timedelta
from typing import List

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
    cache_backend: CacheBackend | None
    use_orjson: bool

    __connections: List[ProxyConnector | None]

    def __init__(
        self,
        api_url: str = "https://songwhip.com/",
        api_timeout: int = 60,
        proxy: List[ProxyConnector] | ProxyConnector | None = None,
        always_use_proxy: bool = False,
        cache_backend: CacheBackend
        | None = FileBackend(
            expire_after=timedelta(days=31),
            ignored_parameters=["key"],
            allowed_codes=(200,),
            allowed_methods=["GET", "POST"],
            cache_control=False,
            use_temp=True,
        ),
        use_orjson: bool = True,
    ) -> None:
        """
        Initialize the SongWhip instance.

        :param api_url: The base URL of the SongWhip API.
        :param api_timeout: Timeout for API requests in seconds.
        :param proxy: Proxy connector(s) to use for requests.
        :param always_use_proxy: Flag indicating whether to always use the provided proxy.
        :param cache_backend: Cache backend to use for caching API responses.
        :param use_orjson: Flag indicating whether to use orjson for JSON serialization.
        """
        self.api_url = api_url.rstrip("/")
        self.api_timeout = api_timeout
        self.proxy = proxy
        self.always_use_proxy = always_use_proxy
        self.cache_backend = cache_backend
        self.use_orjson = use_orjson

        self.__connections: List[ProxyConnector | None] = []
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
        async with CachedSession(
            connector=random.choice(self.__connections),
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
                    data = orjson.loads(await response.read())["data"]["item"]
                except Exception as e:
                    raise APIException(status_code=response.status, message=str(e))

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

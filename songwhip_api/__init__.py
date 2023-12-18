import datetime
import random
import urllib.parse
from typing import List, Dict, Any

import orjson
import pkg_resources
from aiohttp_client_cache import CachedSession, FileBackend, CacheBackend
from aiohttp_proxy import ProxyConnector

from songwhip_api.types import (
    EntityType,
    Artist,
    Album,
    Track,
    Link,
    PlatformName,
)
from songwhip_api.types.exceptions import APIException

try:
    __version__ = pkg_resources.get_distribution("songwhip_api").version
except pkg_resources.DistributionNotFound:
    __version__ = ""


def parse_links(data: Dict[str, List[dict]]) -> List[Link]:
    results = []
    for platform_name, platform_links in data.items():
        if platform_name not in list(PlatformName):
            continue

        for platform_link in platform_links:
            results.append(
                Link(
                    platform=PlatformName(platform_name),
                    link=platform_link["link"],
                    countries=platform_link.get("countries"),
                )
            )
    return results


def parse_artist(data: Dict[str, Any]) -> Artist:
    return Artist(
        type=EntityType.ARTIST,
        id=data["id"],
        path=data["path"],
        name=data["name"],
        description=data.get("description"),
        source_url=data["sourceUrl"],
        source_country=data["sourceCountry"],
        url=data["url"],
        image=data.get("image"),
        created_at=datetime.datetime.fromisoformat(data["createdAt"]),
        updated_at=datetime.datetime.fromisoformat(data["updatedAt"])
        if data.get("updatedAt")
        else None,
        isrc=data.get("irsc"),
        is_explicit=data.get("isExplicit"),
        links=parse_links(data.get("links", {})),
        links_countries=data.get("linksCountries"),
    )


def parse_track(data: Dict[str, Any]) -> Track:
    return Track(
        type=EntityType.TRACK,
        id=data["id"],
        path=data["path"],
        name=data["name"],
        source_url=data["sourceUrl"],
        source_country=data["sourceCountry"],
        url=data["url"],
        release_date=datetime.datetime.fromisoformat(data["releaseDate"]),
        created_at=datetime.datetime.fromisoformat(data["createdAt"]),
        updated_at=datetime.datetime.fromisoformat(data["updatedAt"])
        if data.get("updatedAt")
        else None,
        image=data.get("image"),
        isrc=data.get("irsc"),
        is_explicit=data.get("isExplicit"),
        links=parse_links(data.get("links", {})),
        links_countries=data.get("linksCountries"),
        artists=[parse_artist(artist_data) for artist_data in data.get("artists", [])],
    )


def parse_album(data: Dict[str, Any]) -> Album:
    return Album(
        type=EntityType.TRACK,
        id=data["id"],
        path=data["path"],
        name=data["name"],
        source_url=data["sourceUrl"],
        source_country=data["sourceCountry"],
        url=data["url"],
        release_date=datetime.datetime.fromisoformat(data["releaseDate"]),
        created_at=datetime.datetime.fromisoformat(data["createdAt"]),
        updated_at=datetime.datetime.fromisoformat(data["updatedAt"])
        if data.get("updatedAt")
        else None,
        image=data.get("image"),
        upc=data.get("upc"),
        is_explicit=data.get("isExplicit"),
        links=parse_links(data.get("links", {})),
        links_countries=data.get("linksCountries"),
        artists=[parse_artist(artist_data) for artist_data in data.get("artists", [])],
    )


class SongWhip:
    def __init__(
        self,
        api_url: str = "https://songwhip.com/",
        api_timeout: int = 60,
        proxy: List[str] | str | None = None,
        always_use_proxy: bool = False,
        cache_backend: CacheBackend
        | None = FileBackend(
            expire_after=900,
            ignored_parameters=["key"],
            allowed_codes=(200,),
            allowed_methods=["GET", "POST"],
            cache_control=False,
        ),
        use_orjson: bool = True,
    ) -> None:
        self.api_url = api_url.rstrip("/")
        self.api_timeout: int = api_timeout
        self.cache_backend: CacheBackend | None = cache_backend
        self.connections: List[str | None] = []
        if proxy is not None:
            for _proxy in proxy if isinstance(proxy, list) else [proxy]:
                self.connections.append(_proxy)
        if not always_use_proxy:
            self.connections.append(None)
        if not self.connections:
            raise ValueError("No connections specified.")
        self.use_orjson: bool = use_orjson

    def __repr__(self) -> str:
        return f"<SongWhip at {hex(id(self))}>"

    async def request(self, url: str) -> Album | Track | Artist:
        connection = random.choice(self.connections)

        async with CachedSession(
            connector=None
            if connection is None
            else ProxyConnector.from_url(connection),
            cache=self.cache_backend,
            headers={
                "User-Agent": f"SongWhipAPI/v{__version__}",
            },
        ) as session:
            async with session.post(
                url=f"{self.api_url}/api/songwhip/create",
                headers={
                    "Content-Type": "application/json",
                    "Referer": f"{self.api_url}/convert?url={urllib.parse.quote(url)}&sourceAction=pasteUrl",
                },
                data=orjson.dumps({"url": url, "country": "US"}),
                timeout=self.api_timeout,
            ) as response:
                try:
                    data = orjson.loads(await response.read())["data"]["item"]
                except Exception:
                    data = {}

            if response.status != 200 or data == {}:
                raise APIException(
                    status_code=response.status, message=data.get("status")
                )

            match EntityType(data["type"]):
                case EntityType.TRACK:
                    return parse_track(data)
                case EntityType.ARTIST:
                    return parse_artist(data)
                case EntityType.ALBUM:
                    return parse_album(data)
                case _:
                    raise APIException(status_code=404)

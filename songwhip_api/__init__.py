from typing import List
from bs4 import BeautifulSoup

from songwhip_api.types import (
    EntityType,
    Response,
    Artist,
    Album,
    Track,
    Link,
    PlatformName,
)
from songwhip_api.types.exceptions import APIException

from aiohttp.typedefs import DEFAULT_JSON_DECODER
from aiohttp_client_cache import CachedSession, FileBackend, CacheBackend
from aiohttp_proxy import ProxyConnector

import orjson
import pkg_resources
import datetime
import random
import pytz

try:
    __version__ = pkg_resources.get_distribution("songwhip_api").version
except pkg_resources.DistributionNotFound:
    __version__ = ""


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

    async def private_request(self, url: str) -> Response:
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
            async with session.get(
                url=f"{self.api_url}/{url}",
                timeout=self.api_timeout,
            ) as response:
                soup = BeautifulSoup(await response.read(), "html5lib")

                try:
                    data = (
                        orjson.loads(
                            soup.find("script", {"id": "__NEXT_DATA__"}).string.encode()
                        )
                        .get("props", {})
                        .get("initialReduxState", {})
                    )
                except Exception:
                    data = {}

            if response.status != 200 or data == {}:
                raise APIException(status_code=response.status)

            return Response(
                artists=[
                    Artist(
                        type=artist["value"]["type"],
                        id=artist["value"]["id"],
                        path=artist["value"]["path"],
                        page_path=artist["value"]["pagePath"],
                        name=artist["value"]["name"],
                        image=artist["value"].get("image"),
                        links=[
                            Link(
                                platform=platform,
                                link=link[0]["link"].format(
                                    country=artist["value"]["sourceCountry"]
                                )
                                if "{country}" in link[0]["link"]
                                else link[0]["link"],
                                countries=link[0]["countries"],
                            )
                            for platform, link in artist["value"]["links"].items()
                            if platform in list(PlatformName)
                        ],
                        has_links=list(
                            filter(
                                lambda e: e in list(PlatformName),
                                artist["value"]["links"].keys(),
                            )
                        ),
                        description=artist["value"].get("description"),
                        links_countries=artist["value"].get("linksCountries"),
                        souce_country=artist["value"]["sourceCountry"],
                        spotify_id=artist["value"].get("spotifyId"),
                        created_at_timestamp=datetime.datetime.fromtimestamp(
                            artist["value"]["createdAtTimestamp"] / 1000, pytz.utc
                        ),
                        refreshed_at_timestamp=datetime.datetime.fromtimestamp(
                            artist["value"]["refreshedAtTimestamp"] / 1000,
                            pytz.utc,
                        )
                        if artist["value"].get("refreshedAtTimestamp") is not None
                        else None,
                        is_partial=artist["isPartial"],
                    )
                    for artist in data.get("artists", {}).values()
                ],
                albums=[
                    Album(
                        type=album["value"]["type"],
                        id=album["value"]["id"],
                        path=album["value"]["path"],
                        page_path=album["value"]["pagePath"],
                        name=album["value"]["name"],
                        image=album["value"]["image"],
                        links=[
                            Link(
                                platform=platform,
                                link=link[0]["link"].format(
                                    country=album["value"]["sourceCountry"]
                                )
                                if "{country}" in link[0]["link"]
                                else link[0]["link"],
                                countries=link[0]["countries"],
                            )
                            for platform, link in album["value"]["links"].items()
                            if platform in list(PlatformName)
                        ],
                        has_links=list(
                            filter(
                                lambda e: e in list(PlatformName),
                                album["value"]["links"].keys(),
                            )
                        ),
                        links_countries=album["value"].get("linksCountries"),
                        souce_country=album["value"]["sourceCountry"],
                        spotify_id=album["value"].get("spotifyId"),
                        created_at_timestamp=datetime.datetime.fromtimestamp(
                            album["value"]["createdAtTimestamp"] / 1000, pytz.utc
                        ),
                        refreshed_at_timestamp=datetime.datetime.fromtimestamp(
                            album["value"]["refreshedAtTimestamp"] / 1000,
                            pytz.utc,
                        )
                        if album["value"].get("refreshedAtTimestamp") is not None
                        else None,
                    )
                    for album in data.get("albums", {}).values()
                ],
                tracks=[
                    Track(
                        type=track["value"]["type"],
                        id=track["value"]["id"],
                        path=track["value"]["path"],
                        page_path=track["value"]["pagePath"],
                        name=track["value"]["name"],
                        image=track["value"]["image"],
                        links=[
                            Link(
                                platform=platform,
                                link=link[0]["link"].format(
                                    country=track["value"]["sourceCountry"]
                                )
                                if "{country}" in link[0]["link"]
                                else link[0]["link"],
                                countries=link[0]["countries"],
                            )
                            for platform, link in track["value"]["links"].items()
                            if platform in list(PlatformName)
                        ],
                        has_links=list(
                            filter(
                                lambda e: e in list(PlatformName),
                                track["value"]["links"].keys(),
                            )
                        ),
                        links_countries=track["value"].get("linksCountries"),
                        souce_country=track["value"]["sourceCountry"],
                        created_at_timestamp=datetime.datetime.fromtimestamp(
                            track["value"]["createdAtTimestamp"] / 1000, pytz.utc
                        ),
                        refreshed_at_timestamp=datetime.datetime.fromtimestamp(
                            track["value"]["refreshedAtTimestamp"] / 1000,
                            pytz.utc,
                        )
                        if track["value"].get("refreshedAtTimestamp") is not None
                        else None,
                        artist_ids=track["value"]["artistIds"],
                    )
                    for track in data.get("tracks", {}).values()
                ],
            )

    async def public_request(
        self,
        url: str,
    ) -> Response:
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
                url=self.api_url,
                timeout=self.api_timeout,
                data=orjson.dumps({"url": url}),
            ) as response:
                try:
                    data = await response.json(
                        loads=orjson.loads if self.use_orjson else DEFAULT_JSON_DECODER
                    )
                except Exception:
                    data = {}

            if response.status != 200 or not data:
                raise APIException(
                    status_code=response.status_code,
                    message=await response.text() if await response.text() else None,
                )

            if data["type"] == EntityType.track:
                return Response(
                    artists=[
                        Artist(
                            type=artist["type"],
                            id=artist["id"],
                            path=artist["path"],
                            page_path=artist["pagePath"],
                            name=artist["name"],
                            image=artist["image"],
                            links=[
                                Link(
                                    platform=platform,
                                    link=link[0]["link"].format(
                                        country=artist["sourceCountry"]
                                    )
                                    if "{country}" in link[0]["link"]
                                    else link[0]["link"],
                                    countries=link[0]["countries"],
                                )
                                for platform, link in artist["links"].items()
                                if platform in list(PlatformName)
                            ],
                            has_links=list(
                                filter(
                                    lambda e: e in list(PlatformName),
                                    artist["links"].keys(),
                                )
                            ),
                            description=artist.get("description"),
                            links_countries=artist.get("linksCountries"),
                            souce_country=artist["sourceCountry"],
                            spotify_id=artist.get("spotifyId"),
                            created_at_timestamp=datetime.datetime.fromtimestamp(
                                artist["createdAtTimestamp"] / 1000, pytz.utc
                            ),
                            refreshed_at_timestamp=datetime.datetime.fromtimestamp(
                                artist["refreshedAtTimestamp"] / 1000,
                                pytz.utc,
                            )
                            if artist.get("refreshedAtTimestamp") is not None
                            else None,
                            is_partial=None,
                        )
                        for artist in data.get("artists", [])
                    ],
                    albums=[],
                    tracks=[
                        Track(
                            type=data["type"],
                            id=data["id"],
                            path=data["path"],
                            page_path=data["pagePath"],
                            name=data["name"],
                            image=data["image"],
                            links=None,
                            has_links=list(
                                filter(
                                    lambda e: e in list(PlatformName),
                                    data["links"].keys(),
                                )
                            ),
                            links_countries=data.get("linksCountries"),
                            souce_country=data["sourceCountry"],
                            created_at_timestamp=datetime.datetime.fromtimestamp(
                                data["createdAtTimestamp"] / 1000, pytz.utc
                            ),
                            refreshed_at_timestamp=datetime.datetime.fromtimestamp(
                                data["refreshedAtTimestamp"] / 1000,
                                pytz.utc,
                            )
                            if data.get("refreshedAtTimestamp") is not None
                            else None,
                            artist_ids=list(map(lambda e: e["id"], data["artists"])),
                        )
                    ],
                )

            elif data["type"] == EntityType.album:
                return Response(
                    artists=[
                        Artist(
                            type=artist["type"],
                            id=artist["id"],
                            path=artist["path"],
                            page_path=artist["pagePath"],
                            name=artist["name"],
                            image=artist["image"],
                            links=[
                                Link(
                                    platform=platform,
                                    link=link[0]["link"].format(
                                        country=artist["sourceCountry"]
                                    )
                                    if "{country}" in link[0]["link"]
                                    else link[0]["link"],
                                    countries=link[0]["countries"],
                                )
                                for platform, link in artist["links"].items()
                                if platform in list(PlatformName)
                            ],
                            has_links=list(
                                filter(
                                    lambda e: e in list(PlatformName),
                                    artist["links"].keys(),
                                )
                            ),
                            description=artist.get("description"),
                            links_countries=artist.get("linksCountries"),
                            souce_country=artist["sourceCountry"],
                            spotify_id=artist.get("spotifyId"),
                            created_at_timestamp=datetime.datetime.fromtimestamp(
                                artist["createdAtTimestamp"] / 1000, pytz.utc
                            ),
                            refreshed_at_timestamp=datetime.datetime.fromtimestamp(
                                artist["refreshedAtTimestamp"] / 1000,
                                pytz.utc,
                            )
                            if artist.get("refreshedAtTimestamp") is not None
                            else None,
                            is_partial=None,
                        )
                        for artist in data.get("artists", [])
                    ],
                    albums=[
                        Album(
                            type=data["type"],
                            id=data["id"],
                            path=data["path"],
                            page_path=data["pagePath"],
                            name=data["name"],
                            image=data["image"],
                            links=None,
                            has_links=list(
                                filter(
                                    lambda e: e in list(PlatformName),
                                    data["links"].keys(),
                                )
                            ),
                            links_countries=data.get("linksCountries"),
                            souce_country=data["sourceCountry"],
                            spotify_id=data.get("spotifyId"),
                            created_at_timestamp=datetime.datetime.fromtimestamp(
                                data["createdAtTimestamp"] / 1000, pytz.utc
                            ),
                            refreshed_at_timestamp=datetime.datetime.fromtimestamp(
                                data["refreshedAtTimestamp"] / 1000,
                                pytz.utc,
                            )
                            if data.get("refreshedAtTimestamp") is not None
                            else None,
                        )
                    ],
                    tracks=[],
                )

            elif data["type"] == EntityType.artist:
                return Response(
                    artists=[
                        Artist(
                            type=data["type"],
                            id=data["id"],
                            path=data["path"],
                            page_path=data["pagePath"],
                            name=data["name"],
                            image=data["image"],
                            links=[
                                Link(
                                    platform=platform,
                                    link=link[0]["link"].format(
                                        country=data["sourceCountry"]
                                    )
                                    if "{country}" in link[0]["link"]
                                    else link[0]["link"],
                                    countries=link[0]["countries"],
                                )
                                for platform, link in data["links"].items()
                                if platform in list(PlatformName)
                            ],
                            has_links=list(
                                filter(
                                    lambda e: e in list(PlatformName),
                                    data["links"].keys(),
                                )
                            ),
                            description=data.get("description"),
                            links_countries=data.get("linksCountries"),
                            souce_country=data["sourceCountry"],
                            spotify_id=data.get("spotifyId"),
                            created_at_timestamp=datetime.datetime.fromtimestamp(
                                data["createdAtTimestamp"] / 1000, pytz.utc
                            ),
                            refreshed_at_timestamp=datetime.datetime.fromtimestamp(
                                data["refreshedAtTimestamp"] / 1000,
                                pytz.utc,
                            )
                            if data.get("refreshedAtTimestamp") is not None
                            else None,
                            is_partial=None,
                        )
                    ],
                    albums=[],
                    tracks=[],
                )

from bs4 import BeautifulSoup

from songwhip_api.types import EntityType, Response
from songwhip_api.types import Artist
from songwhip_api.types import Album
from songwhip_api.types import Track
from songwhip_api.types import Link
from songwhip_api.types import PlatformName

from songwhip_api.utils.cache import TTLCache

import pytz
import httpx_cache
import orjson
import pkg_resources
import datetime

from songwhip_api.types.exceptions import APIException


try:
    __version__ = pkg_resources.get_distribution("songwhip_api").version
except pkg_resources.DistributionNotFound:
    __version__ = ""


class SongWhip:
    def __init__(
        self,
        api_url: str = "https://songwhip.com/",
        api_timeout: int = 60,
        use_cache: bool = True,
        cache_time: int = 900,
    ) -> None:
        self.api_url = api_url.rstrip("/")
        self.api_timeout = api_timeout
        self.use_cache = use_cache
        self.cache_time = cache_time

    def __repr__(self) -> str:
        return f"<SongWhip at {hex(id(self))}>"

    async def private_request(self, url: str) -> Response:
        async with httpx_cache.AsyncClient(
            headers={
                "User-Agent": f"SongWhipAPI/v{__version__}",
                "cache-control": f"max-age={self.cache_time}"
                if self.use_cache
                else "no-cache",
            },
            cache=httpx_cache.FileCache(),
            follow_redirects=True,
        ) as client:
            request = client.build_request(
                "GET",
                "{}/{}".format(self.api_url, url),
                timeout=self.api_timeout,
            )
            response = await client.send(request)
            soup = BeautifulSoup(response.content, "html5lib")

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

            if response.status_code != 200 or data == {}:
                raise APIException(status_code=response.status_code)

            return Response(
                artists=[
                    Artist(
                        type=artist["value"]["type"],
                        id=artist["value"]["id"],
                        path=artist["value"]["path"],
                        page_path=artist["value"]["pagePath"],
                        name=artist["value"]["name"],
                        image=artist["value"]["image"],
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

    @TTLCache(time_to_live=900, maxsize=1024)
    async def public_request(
        self,
        url: str,
    ) -> Response:
        async with httpx_cache.AsyncClient(
            headers={
                "User-Agent": f"SongWhipAPI/v{__version__}",
                "cache-control": "no-cache",
            },
            cache=None,
        ) as client:
            request = client.build_request(
                "POST",
                self.api_url,
                timeout=self.api_timeout,
                data=orjson.dumps({"url": url}),
            )
            response = await client.send(request)

            try:
                data = orjson.loads(response.content)
            except Exception:
                data = {}

            if response.status_code != 200 or data == {}:
                raise APIException(
                    status_code=response.status_code,
                    message=response.content.decode() if response.content else None,
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

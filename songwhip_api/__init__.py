from bs4 import BeautifulSoup

from songwhip_api.types import Response
from songwhip_api.types import Artist
from songwhip_api.types import Album
from songwhip_api.types import Track
from songwhip_api.types import Link
from songwhip_api.types import PlatformName

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

    async def public_request(
        self,
        url: str,
    ):
        """
        TODO
        """
        return await self.private_request(url=url)

from enum import Enum

from typing import List
from typing import Optional

from pydantic import BaseModel

import datetime


class PlatformName(str, Enum):
    DEEZER = "deezer"
    TIDAL = "tidal"
    ITUNES = "itunesStore"
    SPOTIFY = "spotify"
    TWITTER = "twitter"
    APPLE_MUSIC = "itunes"
    YOUTUBE = "youtube"
    YOUTUBE_MUSIC = "youtubeMusic"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    MUSICBRAINZ = "musicBrainz"
    WIKIPEDIA = "wikipedia"
    DISCOGS = "discogs"
    QOBUZ = "qobuz"
    PANDORA = "pandora"
    AMAZON_STORE = "amazon"
    AMAZON_MUSIC = "amazonMusic"
    NAPSTER = "napster"
    AUDIUS = "audius"
    AUDIOMACK = "audiomack"
    GAANA = "gaana"
    TIKTOK = "tiktok"
    LINE_MUSIC = "lineMusic"
    BANDCAMP = "bandcamp"
    JIO_SAAVN = "jioSaavn"
    SOUNDCLOUD = "soundcloud"


class Link(BaseModel):
    platform: PlatformName
    link: str
    countries: Optional[List[str]]

    class Config:
        use_enum_values = True


class EntityType(str, Enum):
    artist = "artist"
    album = "album"
    track = "track"


class Entity(BaseModel):
    type: EntityType
    id: int
    path: str
    page_path: str
    name: str
    image: str | None
    has_links: List[PlatformName]
    links: Optional[List[Link]]
    links_countries: Optional[List[str]]
    souce_country: str
    created_at_timestamp: datetime.datetime
    refreshed_at_timestamp: Optional[datetime.datetime]

    class Config:
        use_enum_values = True

    def get_url(self, basic_url: str = "https://songwhip.com") -> str:
        return basic_url + self.page_path


class Artist(Entity):
    description: Optional[str]
    spotify_id: Optional[str]
    is_partial: Optional[bool]

    class Config:
        use_enum_values = True


class Album(Entity):
    spotify_id: Optional[str]

    class Config:
        use_enum_values = True


class Track(Entity):
    artist_ids: List[int]

    class Config:
        use_enum_values = True


class Response(BaseModel):
    artists: List[Artist]
    albums: List[Album]
    tracks: List[Track]

import datetime
from enum import Enum
from typing import List
from typing import Optional

from pydantic import BaseModel


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
    ARTIST = "artist"
    ALBUM = "album"
    TRACK = "track"


class Entity(BaseModel):
    type: EntityType
    id: int
    path: str
    name: str
    url: str
    source_url: str
    source_country: str
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime]
    image: str | None
    links: Optional[List[Link]]
    links_countries: Optional[List[str]]

    class Config:
        use_enum_values = True

    def get_url(self, basic_url: str = "https://songwhip.com") -> str:
        return basic_url + self.url


class Artist(Entity):
    description: Optional[str]

    class Config:
        use_enum_values = True


class Album(Entity):
    release_date: datetime.datetime
    upc: str | None

    class Config:
        use_enum_values = True


class Track(Entity):
    release_date: datetime.datetime
    isrc: str | None
    is_explicit: bool | None
    artists: List[Artist]

    class Config:
        use_enum_values = True

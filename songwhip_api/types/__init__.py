from enum import Enum

from typing import List
from typing import Optional

from pydantic import BaseModel

import datetime


class PlatformName(str, Enum):
    deezer = "deezer"
    tidal = "tidal"
    itunes = "itunesStore"
    spotify = "spotify"
    twitter = "twitter"
    apple_music = "itunes"
    youtube = "youtube"
    youtube_music = "youtubeMusic"
    facebook = "facebook"
    instagram = "instagram"
    musicbrainz = "musicBrainz"
    wikipedia = "wikipedia"
    discogs = "discogs"
    qobuz = "qobuz"
    pandora = "pandora"
    amazon_store = "amazon"
    amazon_music = "amazonMusic"
    napster = "napster"
    audius = "audius"
    audiomack = "audiomack"
    gaana = "gaana"
    tiktok = "tiktok"
    line_music = "lineMusic"
    bandcamp = "bandcamp"
    jio_saavn = "jioSaavn"
    soundcloud = "soundcloud"


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
    image: str
    has_links: List[PlatformName]
    links: List[Link]
    links_countries: Optional[List[str]]
    souce_country: str
    created_at_timestamp: datetime.datetime
    refreshed_at_timestamp: Optional[datetime.datetime]

    class Config:
        use_enum_values = True


class Artist(Entity):
    description: Optional[str]
    spotify_id: Optional[str]
    is_partial: bool

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

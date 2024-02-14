from datetime import datetime
from typing import Dict, Any
from typing import List

from .artist import Artist
from .entity import Entity
from .link import Link
from ..enums.entity_type import EntityType


class Track(Entity):
    """
    Represents a track in the music catalog.

    :ivar type: The type of the entity (an instance of EntityType).
    :ivar id: The unique identifier of the entity.
    :ivar path: The path of the entity.
    :ivar name: The name of the entity.
    :ivar url: The URL of the entity.
    :ivar source_url: The source URL of the entity.
    :ivar source_country: The country of origin of the entity.
    :ivar created_at: The datetime when the entity was created.
    :ivar updated_at: The datetime when the entity was last updated, if available.
    :ivar image: The URL of the image associated with the entity, if available.
    :ivar links: A list of links associated with the entity, if available.
    :ivar links_countries: A list of countries associated with the links, if available.
    :ivar release_date: The release date of the track.
    :ivar isrc: The International Standard Recording Code (ISRC) of the track, if available.
    :ivar is_explicit: Indicates whether the track contains explicit content.
    :ivar artists: A list of artists associated with the track.
    """

    release_date: datetime
    isrc: str | None
    is_explicit: bool | None
    artists: List[Artist]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Track":
        """
        Create a Track instance from a dictionary.

        :param data: A dictionary containing track data.

        :return: An instance of the Track class.
        """
        return Track(
            type=EntityType.TRACK,
            id=data["id"],
            path=data["path"],
            name=data["name"],
            source_url=data["sourceUrl"],
            source_country=data["sourceCountry"],
            url=data["url"],
            release_date=datetime.fromisoformat(data["releaseDate"]),
            created_at=datetime.fromisoformat(data["createdAt"]),
            updated_at=datetime.fromisoformat(data["updatedAt"])
            if data.get("updatedAt")
            else None,
            image=data.get("image"),
            isrc=data.get("irsc"),
            is_explicit=data.get("isExplicit"),
            links=Link.from_dict(data.get("links", {})),
            links_countries=data.get("linksCountries"),
            artists=[
                Artist.from_dict(artist_data) for artist_data in data.get("artists", [])
            ],
        )


__all__ = ("Track",)

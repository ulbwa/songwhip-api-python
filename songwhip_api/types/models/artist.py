from datetime import datetime
from typing import Dict, Any

from .entity import Entity
from .link import Link
from ..enums.entity_type import EntityType


class Artist(Entity):
    """
    Represents an artist in the music catalog.

    :ivar type: The type of the artist (an instance of EntityType).
    :ivar id: The unique identifier of the artist.
    :ivar path: The path of the artist.
    :ivar name: The name of the artist.
    :ivar description: The description of the artist, if available.
    :ivar source_url: The source URL of the artist.
    :ivar source_country: The country of origin of the artist.
    :ivar url: The URL of the artist.
    :ivar image: The URL of the image associated with the artist, if available.
    :ivar created_at: The datetime when the artist was created.
    :ivar updated_at: The datetime when the artist was last updated, if available.
    :ivar links: A list of links associated with the artist, if available.
    :ivar links_countries: A list of countries associated with the links, if available.
    """

    description: str | None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Artist":
        """
        Create an Artist instance from a dictionary.

        :param data: A dictionary containing artist data.

        :return: An instance of the Artist class.
        """
        return cls(
            type=EntityType.ARTIST,
            id=data["id"],
            path=data["path"],
            name=data["name"],
            description=data.get("description"),
            source_url=data["sourceUrl"],
            source_country=data["sourceCountry"],
            url=data["url"],
            image=data.get("image"),
            created_at=datetime.fromisoformat(data["createdAt"]),
            updated_at=datetime.fromisoformat(data["updatedAt"])
            if data.get("updatedAt")
            else None,
            isrc=data.get("irsc"),
            is_explicit=data.get("isExplicit"),
            links=Link.from_dict(data.get("links", {})),
            links_countries=data.get("linksCountries"),
        )


__all__ = ("Artist",)

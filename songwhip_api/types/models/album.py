from datetime import datetime
from typing import Dict, Any, List

from .artist import Artist
from .entity import Entity
from .link import Link
from ..enums.entity_type import EntityType


class Album(Entity):
    """
    Represents an album in the music catalog.

    :ivar type: The type of the album (an instance of EntityType).
    :ivar id: The unique identifier of the album.
    :ivar path: The path of the album.
    :ivar name: The name of the album.
    :ivar url: The URL of the album.
    :ivar source_url: The source URL of the album.
    :ivar source_country: The country of origin of the album.
    :ivar created_at: The datetime when the album was created.
    :ivar updated_at: The datetime when the album was last updated, if available.
    :ivar image: The URL of the image associated with the album, if available.
    :ivar links: A list of links associated with the album, if available.
    :ivar links_countries: A list of countries associated with the links, if available.
    :ivar release_date: The release date of the album.
    :ivar upc: The Universal Product Code (UPC) of the album, if available.
    :ivar is_explicit: Indicates whether the album contains explicit content.
    :ivar artists: A list of artists associated with the album.
    """

    release_date: datetime
    upc: str | None
    is_explicit: bool | None
    artists: List[Artist]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Album":
        """
        Create an Album instance from a dictionary.

        :param data: A dictionary containing album data.

        :return: An instance of the Album class.
        """
        return Album(
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
            upc=data.get("upc"),
            is_explicit=data.get("isExplicit"),
            links=Link.from_dict(data.get("links", {})),
            links_countries=data.get("linksCountries"),
            artists=[
                Artist.from_dict(artist_data) for artist_data in data.get("artists", [])
            ],
        )


__all__ = ("Album",)

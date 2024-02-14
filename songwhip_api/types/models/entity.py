from abc import ABC
from datetime import datetime
from typing import List

from pydantic import BaseModel

from .link import Link
from ..enums.entity_type import EntityType


class Entity(ABC, BaseModel):
    """
    Base class representing an entity in the music catalog.

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
    """

    type: EntityType
    id: int
    path: str
    name: str
    url: str
    source_url: str
    source_country: str
    created_at: datetime
    updated_at: datetime | None
    image: str | None
    links: List[Link] | None
    links_countries: List[str] | None


__all__ = ("Entity",)

from enum import StrEnum


class EntityType(StrEnum):
    """
    An enumeration representing different types of entities in a music catalog.

    :cvar ARTIST: Represents an entity type for an artist.
    :cvar ALBUM: Represents an entity type for an album.
    :cvar TRACK: Represents an entity type for a track.
    """

    ARTIST = "artist"
    ALBUM = "album"
    TRACK = "track"


__all__ = ("EntityType",)

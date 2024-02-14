from enum import StrEnum


class PlatformName(StrEnum):
    """
    An enumeration representing platform names.

    Each platform name corresponds to a specific digital music service or social media platform.
    """

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


__all__ = ("PlatformName",)

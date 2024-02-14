from typing import List, Dict, Any

from pydantic import BaseModel

from ..enums.platform_name import PlatformName
from ... import logger


class Link(BaseModel):
    """
    Represents a link associated with a specific platform.

    :ivar platform: The name of the platform (an instance of PlatformName).
    :ivar link: The URL link associated with the platform.
    :ivar countries: A list of countries where the link is available, if specified.
    """

    platform: PlatformName
    link: str
    countries: List[str] | None

    @staticmethod
    def from_dict(data: Dict[str, List[Dict[str, Any]]]) -> List["Link"]:
        """
        Create a list of Link instances from a dictionary.

        :param data: A dictionary containing platform links.

        :return: A list of Link instances.
        """
        results: List[Link] = []

        for platform_name, platform_links in data.items():
            if platform_name not in list(PlatformName):
                logger.warning(f"Link does not support {platform_name=}.")
                continue

            for platform_link in platform_links:
                results.append(
                    Link(
                        platform=PlatformName(platform_name),
                        link=platform_link["link"],
                        countries=platform_link.get("countries"),
                    )
                )

        return results


__all__ = ("Link",)


from secrets_handler import SecretsHandler
from spotipy import CacheHandler


class MemoryCacheHandler(CacheHandler):
    """
    A cache handler that simply stores the token info in memory as an
    instance attribute of this class. The token info will be lost when this
    instance is freed.
    """

    def __init__(self, token_info: dict[str, str | int] | None = None):
        """
        Initializes the cache handler

        Parameters
        ----------
        token_info : dict[str, str | int], default=None
            The token info to store in memory
        """
        self.token_info = token_info

    def get_cached_token(self) -> dict[str, str | int] | None:
        """
        Retrieves the cached token

        Returns
        -------
        dict[str, str | int] | None
            The token_info if it exists
        """
        return self.token_info

    def save_token_to_cache(self, token_info: dict[str, str | int]) -> None:
        """
        Saves a given token to the cache

        Parameters
        ----------
        token_info : dict[str, str | int]
            The token info to store in memory
        """
        self.token_info = token_info


class BaseClientCacheHandler(CacheHandler):
    """
    A cache handler that simply stores the token info in memory as an
    instance attribute of this class. The token info will be lost when this
    instance is freed.
    """

    def __init__(self) -> None:
        pass

    def get_cached_token(self) -> str:
        """
        Retrieves the base client's stored token
        """
        return SecretsHandler.get_spotify_base_token()

    def save_token_to_cache(self, token_info: str) -> None:
        """
        Saves a given token as belonging to the base client

        Parameters
        ----------
        token_info : str
            A string denoting the token's info
        """
        SecretsHandler.save_spotify_base_token(token_info)

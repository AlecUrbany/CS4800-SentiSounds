
import asyncio
from secrets_handler import SecretsHandler
from spotipy import CacheHandler
from auth_handler import AuthHandler

class MemoryCacheHandler(CacheHandler):
    """
    A cache handler that simply stores the token info in memory as an
    instance attribute of this class. The token info will be lost when this
    instance is freed.
    """

    def __init__(self, user_email: str) -> None:
        """
        Parameters:
            * username: The username of the user in the database (email PK) to cache the token for
        """
        self.user_email = user_email

    def get_cached_token(self):
        return asyncio.run(AuthHandler.get_spotify_token(self.user_email))

    def save_token_to_cache(self, token_info: dict):
        asyncio.run(AuthHandler.save_spotify_token(self.user_email, token_info))

class BaseClientCacheHandler(CacheHandler):
    """
    A cache handler that simply stores the token info in memory as an
    instance attribute of this class. The token info will be lost when this
    instance is freed.
    """

    def __init__(self) -> None:
        pass

    def get_cached_token(self):
        return SecretsHandler.get_spotify_base_token()

    def save_token_to_cache(self, token_info):
        SecretsHandler.save_spotify_base_token(token_info)
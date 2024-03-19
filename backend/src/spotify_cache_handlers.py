
from secrets_handler import SecretsHandler
from spotipy import CacheHandler

class MemoryCacheHandler(CacheHandler):
    """
    A cache handler that simply stores the token info in memory as an
    instance attribute of this class. The token info will be lost when this
    instance is freed.
    """

    def __init__(self, token_info=None):
        """
        Parameters:
            * token_info: The token info to store in memory. Can be None.
        """
        self.token_info = token_info

    def get_cached_token(self):
        return self.token_info

    def save_token_to_cache(self, token_info):
        self.token_info = token_info

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
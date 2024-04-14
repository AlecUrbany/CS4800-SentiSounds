from  googleapiclient import discovery
from secrets_handler import SecretsHandler
import queue
import time
import threading


class YoutubeHandler:
    """
    A handler for interacting with the YouTube API.

    Contains a definition for a static _client_instance. This should only be
    accessed via the `youtube` field, which will automatically fill this field
    if it does not yet exist. Any other accesses to this instance are unsafe
    and should not be used.


    """
    api_service_name = "youtube"
    api_version = "v3"
    MAX_THREAD_COUNT = 5
    _youtube_instance: discovery.Resource | None = None

    def __init__():
        """
        Raises a TypeError.
        YoutubeHandler instances must not be created as this is a singleton
        """
        raise TypeError(
            "YoutubeHandler instances should not be created. " +
            "Consider using the `get_client()` function."
        )
    @staticmethod
    def get_client():
        """
        Retrieves or creates the YouTube client instance

        Returns
        -------
        googleapiclient.discovery.Resource
            The static YouTube client
        """
        if YoutubeHandler._youtube_instance:
            return YoutubeHandler._youtube_instance

        return YoutubeHandler._initialize_client()
    @staticmethod
    def _initialize_client():
        """
        Initializes the YouTube client.
        """
        _youtube_instance = discovery.build(
            YoutubeHandler.api_service_name,
            YoutubeHandler.api_version,
            developerKey=SecretsHandler.get_youtube_key()
        )
        return _youtube_instance

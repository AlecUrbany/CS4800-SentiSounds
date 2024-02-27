from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
from secrets_handler import SecretsHandler
import random

class SpotifyHandler:
    """
    A static class to handle all Spotify API interactions.

    Contains a definition for a static _client_instance. This should only be
    accessed via the `get_client()` function, which will automatically fill
    this field if it does not yet exist. Any other accesses to this instance
    are unsafe and should not be used.

    """

    def __init__(self) -> None:
        raise TypeError(
            "SpotifyHandler instances should not be created. " +
            "Consider using the `get_client()` function."
        )

    # A static reference to the Spotify OAuth client
    _client_instance: Spotify | None = None

    @staticmethod
    def get_base_client() -> Spotify:
        """
        Retrieves or creates the Spotify client instance with no user credentials

        Returns
        -------
        Spotify
            The static Spotify client
        """
        if SpotifyHandler._client_instance:
            return SpotifyHandler._client_instance

        return SpotifyHandler._initialize_client()

    @staticmethod
    def _initialize_base_client() -> Spotify:
        """
        Initializes the Spotify client with no user credentials.

        This function should never be called outside of this class. To retrieve
        the client safely, use the `get_client` function.

        Returns
        -------
        Spotify
            The static Spotify client
        """
        SpotifyHandler._client_instance = Spotify(
            client_credentials_manager=SpotifyClientCredentials(
                client_id=SecretsHandler.get_spotify_client_id(),
                client_secret=SecretsHandler.get_spotify_client_secret()
            )
        )
        return SpotifyHandler._client_instance
    
    @staticmethod
    def get_user_client() -> Spotify:
        """
        Retrieves or creates the Spotify client instance with a specific user credentials

        Returns
        -------
        Spotify
            The static Spotify client
        """
        if SpotifyHandler._client_instance:
            return SpotifyHandler._client_instance

        return SpotifyHandler._initialize_user_client()
    
    @staticmethod
    def _initialize_user_client() -> Spotify:
        """
        Initializes the Spotify client with user credentials.

        This function should never be called outside of this class. To retrieve
        the client safely, use the `get_client` function.

        Returns
        -------
        Spotify
            The static Spotify client with user credentials
        """
        redirect_uri = "https://github.com/AlecUrbany/CS4800-SentiSounds"
        scope = ["streaming", "playlist-modify-private", "user-top-read", "user-read-private"]
        SpotifyHandler._client_instance = Spotify(
            auth_manager=SpotifyOAuth(
                scope=scope,
                redirect_uri=redirect_uri, 
                open_browser=True, # Not sure how to get around the need for the redirect URI to be pasted
                client_id=SecretsHandler.get_spotify_client_id(),
                client_secret=SecretsHandler.get_spotify_client_secret()
            )
        )
        return SpotifyHandler._client_instance

    @staticmethod
    def get_genre_songs(genre: str, market: str, limit: int=10) -> list[dict]:
        """
        Retrieves a pseudo-random list of songs in a genre sourced from the Spotify API.

        Returns
        -------
        list[dict]
            The list of songs from the Spotify API with the following:
            - name: The name of the song
            - preview_url: A URL to a 30-second preview of the song
            - uri: A URI to the song
            - explicit: Whether the song is explicit
            - is_playable: Whether the song is playable
            - popularity: The popularity of the song
        """
        random_offset = random.randint(0, 1000);
        keys_to_extract = ["name", "preview_url", "uri", "explicit", "is_playable", "popularity"]
        tracks_all = SpotifyHandler._client_instance.search(q='genre:' + genre, type="track", market=market, offset=random_offset, limit=limit)["tracks"]["items"]
        return [{key: track[key] for key in keys_to_extract} for track in tracks_all]
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
from secrets_handler import SecretsHandler
import random

class SpotifyHandler:
    """
    A class to handle all Spotify API interactions.

    Contains a definition for a static _client_instance. This should only be
    accessed via the `get_client()` function, which will automatically fill
    this field if it does not yet exist. Any other accesses to this instance
    are unsafe and should not be used.

    """

    def __init__(self) -> None:
        self._client_instance = None
        self.is_user_client = None

    def get_base_client(self) -> Spotify:
        """
        Retrieves or creates the Spotify client instance with no user credentials

        Returns
        -------
        Spotify
            The static Spotify client
        """
        if self._client_instance:
            if self.is_user_client is not None and self.is_user_client is True:
                raise RuntimeError("This instance is a user client, not a base client")
            else:
                return self._client_instance
        else:
            return self._initialize_base_client()

    def _initialize_base_client(self) -> Spotify:
        """
        Initializes the Spotify client with no user credentials.

        This function should never be called outside of this class. To retrieve
        the client safely, use the `get_client` function.

        Returns
        -------
        Spotify
            The static Spotify client
        """
        self.is_user_client = False
        self._client_instance = Spotify(
            client_credentials_manager=SpotifyClientCredentials(
                client_id=SecretsHandler.get_spotify_client_id(),
                client_secret=SecretsHandler.get_spotify_client_secret()
            )
        )
        return self._client_instance

    def get_user_client(self) -> Spotify:
        """
        Retrieves or creates the Spotify client instance with a specific user credentials

        Returns
        -------
        Spotify
            The static Spotify client
        """
        
        if self._client_instance:
            if self.is_user_client is False:
                raise RuntimeError("This instance is a base client, not a user client")
            else:
                return self._client_instance
        else:
            return self._initialize_user_client()

    def _initialize_user_client(self) -> Spotify:
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
        self.is_user_client = True
        self._client_instance = Spotify(
            auth_manager=SpotifyOAuth(
                scope=scope,
                redirect_uri=redirect_uri,
                open_browser=True, # Not sure how to get around the need for the redirect URI to be pasted
                client_id=SecretsHandler.get_spotify_client_id(),
                client_secret=SecretsHandler.get_spotify_client_secret()
            )
        )
        return self._client_instance

    
    def get_genre_songs(self, genre: str, market: str = "from_token", limit: int=10) -> list[dict]:
        """
        Retrieves a pseudo-random list of songs in a genre sourced from the Spotify API.

        Parameters
        ---------- 
        genre : str
            
        market : str
            An ISO 3166-1 alpha-2 country code or the string from_token.
        
        limit : int
            The maximum number of songs to return. Default is 10.

        This list may be user specific, so use the get_available_genre_seeds to find user genres

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
            - id: The ID of the song (useful for creating a playlist)
        """
        random_offset = random.randint(0, 1000)
        keys_to_extract = ["name", "preview_url", "uri", "explicit", "is_playable", "popularity", "id"]
        tracks_all = self._client_instance.search(q='genre:' + genre, type="track", market=market, offset=random_offset, limit=limit)["tracks"]["items"]
        return [{key: track[key] for key in keys_to_extract} for track in tracks_all]
    
    def get_available_genre_seeds(self) -> list[str]:
        """
        Retrieves a list of available genre "seeds" from the Spotify API.

        Returns
        -------
        list[str]
            The list of available genre seeds
        """
        return self._client_instance.recommendation_genre_seeds()["genres"]

    def create_playlist(self, playlist_name: str, description: str, song_ids: list[str]) -> str:
        """
        Creates a playlist for a user on Spotify given a list of song IDs.

        Parameters
        ----------
        playlist_name : str
            The name of the playlist
        description : str
            The description of the playlist, preferably the sentiment prompt provided by the user

        Returns
        -------
        str
            A URL to the created playlist
        """
        if not self.is_user_client:
            raise RuntimeError("This instance is a base client and cannot create a playlist for a user. Use a user client.")
        else:
            playlist = self._client_instance.user_playlist_create(self._client_instance.me()["id"], playlist_name, public=False, description=description)
            id = playlist["id"]
            url = playlist["external_urls"]["spotify"]
            self._client_instance.user_playlist_add_tracks(self._client_instance.me()["id"], id, song_ids)
            return url
from spotipy import Spotify, CacheHandler
from spotipy.oauth2 import SpotifyOAuth
from database_handler import DatabaseHandler
import random
from secrets_handler import SecretsHandler
from spotify_cache_handlers import *
from urllib.parse import urlencode
from spotipy.util import normalize_scope

class SpotifyHandler:
    """
    A class to handle all Spotify API interactions.

    Attributes
    ----------
    _client_instance : Spotify
        The Spotify client instance, should not be accessed directly
    user_email : str
        The email of the user in the database (email PK) to cache the token for, if absent indicates a base client

    """
    BASE_CLIENT = Spotify(
            auth_manager=SpotifyOAuth(
                scope="user-read-private",
                redirect_uri=SecretsHandler.get_spotify_redirect_uri(),
                open_browser=False, # Not sure how to get around the need for the redirect URI to be pasted
                client_id=SecretsHandler.get_spotify_client_id(),
                client_secret=SecretsHandler.get_spotify_client_secret(),
                cache_handler= BaseClientCacheHandler()
            )
    )
    user_scope = [
        "streaming",
        "playlist-modify-private",
        "user-top-read",
        "user-read-private"
    ]

    def __init__(self) -> None:
        self._client_instance: Spotify | None = None
        self.cache_handler = None

    @staticmethod
    def create_OAuth(token_info: dict = None) -> tuple[SpotifyOAuth, CacheHandler]:
        """
        Creates an OAuth handler for Spotify as well as a reference to the cache handler
        """
        cache_handler = MemoryCacheHandler(token_info=token_info)
        return SpotifyOAuth(
            cache_handler= cache_handler,
            scope= SpotifyHandler.user_scope,
            redirect_uri=SecretsHandler.get_spotify_redirect_uri(),
            open_browser=False, # Not sure how to get around the need for the redirect URI to be pasted
            client_id=SecretsHandler.get_spotify_client_id(),
            client_secret=SecretsHandler.get_spotify_client_secret()
        ), cache_handler
    
    @staticmethod
    def generate_auth_url():
        OAUTH_URL = "https://accounts.spotify.com/authorize"
        payload = {
            "client_id": SecretsHandler.get_spotify_client_id(),
            "response_type": "code",
            "redirect_uri": SecretsHandler.get_spotify_redirect_uri(),
            "scope": normalize_scope(SpotifyHandler.user_scope)
        }
        return "%s?%s" % (OAUTH_URL, urlencode(payload))

    def get_client(self) -> Spotify:
        """
        Retrieves or creates a Spotify client. This client can either be
        authenticated or a base client. As such, this function should
        only be used if you're absolutely certain you don't care what
        type of client you're retrieving.

        Returns
        -------
        Spotify
            Whatever Spotify client is available
        """
        if self._client_instance:
            return self._client_instance
        return SpotifyHandler.BASE_CLIENT


    def load_token(self, token_info) -> None:
        """
        Initializes the Spotify client with user credentials.

        This function should never be called outside of this class. To retrieve
        the client safely, use the `get_user_client` function.

        Returns
        -------
        Spotify
            The static Spotify client with user credentials
        """
        auth_manager, self.cache_handler = SpotifyHandler.create_OAuth(token_info=token_info)
        self._client_instance = Spotify(
            auth_manager= auth_manager
        )

    def get_token(self) -> dict | None:
        """
        Gets the token from the cache handler if there has been a token loaded
        """
        if self.cache_handler is None:
            return None
        else:
            return self.cache_handler.get_cached_token()

    def get_genre_songs(
                self,
                genres: list[str],
                market: str = "from_token",
                limit: int = 10
            ) -> list[dict]:
        """
        Retrieves a pseudo-random list of songs in a genre sourced from the Spotify API.

        Parameters
        ----------
        genre : str
            The genre to search songs for
        market : str
            An ISO 3166-1 alpha-2 country code or the string from_token.
        limit : int
            The maximum number of songs to return. Default is 10.

        This list may be user specific, so use the get_available_genre_seeds
        to find user genres

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
        assert type(genres) == list, "Genres must be a list of strings, even a single genre"
        random_offset = random.randint(0, 1000)
        keys_to_extract = [
            "name",
            "preview_url",
            "uri", "explicit",
            "is_playable",
            "popularity",
            "id"
        ]
        search_result = []
        for genre in genres: # This is a list of genres
            part = self.get_client().search( # The search results will be appended to the list
                q='genre:' + genre,
                type="track",
                market=market, offset=random_offset, limit=limit
            )
            part = part["tracks"]["items"]
            search_result += part
        if not search_result:
            raise ValueError(
                "Something went wrong searching for songs from Spotify"
            )
        random.shuffle(search_result)
        pruned_songs = [
            {key: track[key] for key in keys_to_extract} for track in search_result
        ]
        return pruned_songs

    def get_available_genre_seeds(self) -> list[str]:
        """
        Retrieves a list of available genre "seeds" from the Spotify API.

        Returns
        -------
        list[str]
            The list of available genre seeds
        """

        seeds_result = self.get_client().recommendation_genre_seeds()

        if not seeds_result:
            raise ValueError(
                "Something went wrong retrieving genre seeds from Spotify"
            )

        return seeds_result["genres"]

    def create_playlist(
                self,
                playlist_name: str,
                description: str,
                song_ids: list[str]
            ) -> str:
        """
        Creates a playlist for a user on Spotify given a list of song IDs.

        Parameters
        ----------
        playlist_name : str
            The name of the playlist
        description : str
            The description of the playlist, preferably the sentiment prompt
            provided by the user

        Returns
        -------
        str
            A URL to the created playlist
        """

        '''
        if self._client_instance is None:
            raise Exception(
                "No user has been loaded into the Spotify client instance."
            )
        '''
        self._client_instance = SpotifyHandler.BASE_CLIENT
        user_id = self._client_instance.me()["id"]
        playlist = self._client_instance.user_playlist_create(
            user_id,
            playlist_name,
            public=False,
            description=description
        )

        if not playlist:
            raise RuntimeError(
                "Something went wrong creating this playlist"
            )

        self._client_instance.user_playlist_add_tracks(
            user_id, playlist["id"], song_ids
        )

        return playlist["external_urls"]["spotify"]
    


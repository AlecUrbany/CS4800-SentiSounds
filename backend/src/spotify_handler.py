"""A handler for interacting with Spotify's API through the Spotipy wrapper"""

from __future__ import annotations

from urllib.parse import urlencode

from secrets_handler import SecretsHandler
from senti_types import song_type, token_type
from spotify_cache_handlers import BaseClientCacheHandler, MemoryCacheHandler
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.util import normalize_scope
import random


class SpotifyHandler:
    """
    A class to handle all Spotify API interactions.

    There are two types of Spotify clients; a base client and a user client.
    A base client uses the default SentiSounds Spotify account to perform
    Spotify operations. The user client will be able to return results and
    recommendations directly via the Spotify API.

    Attributes
    ----------
    BASE_CLIENT : spotipy.Spotify
        The base Spotify client instance.
        This instance is not authenticated with a particular user
    user_scope : list[str]
        The list of scopes required to access user data
    _client_instance : spotipy.Spotify
        The Spotify client instance, which should not be accessed directly
    cache_handler : MemoryCacheHandler
        The object getting and storing the Spotify authentication token. It is
        exposed here for direct control of the tokens outside of this object
    """

    BASE_CLIENT = Spotify(
        auth_manager=SpotifyOAuth(
            scope="user-read-private",
            redirect_uri=SecretsHandler.get_spotify_redirect_uri(),
            open_browser=False,
            client_id=SecretsHandler.get_spotify_client_id(),
            client_secret=SecretsHandler.get_spotify_client_secret(),
            cache_handler=BaseClientCacheHandler(),
        )
    )
    """Defines the base SentiSounds client for Spotify interactions"""

    user_scope = [
        "streaming",
        "playlist-modify-private",
        "user-top-read",
        "user-read-private",
        "user-library-modify",
        "user-library-read",
    ]
    """The permission scope to request when initializing a user client"""

    def __init__(self) -> None:
        """
        Initializes a base SpotifyHandler instance

        Consider using the `from_token()` classmethod to retrieve the
        user client
        """

        self.cache_handler: MemoryCacheHandler | None = None
        """The cache handler used for user authentication"""

        self._client_instance: Spotify | None = None
        """
        The client instance (Spotify) used to interact with the API
        """

    @classmethod
    def from_token(
        cls: type[SpotifyHandler], token_info: token_type
    ) -> SpotifyHandler:
        """
        Initializes the Spotify client with user credentials.

        Parameters
        ----------
        token_info : token_type
            The token information to load into the cache handler

        Returns
        -------
        SpotifyHandler
            The created SpotifyHandler object
        """
        handler = cls()

        auth_manager, cache_handler = cls.create_oauth(token_info=token_info)
        handler.cache_handler = cache_handler
        handler._client_instance = Spotify(auth_manager=auth_manager)

        return handler

    @staticmethod
    def create_oauth(
        token_info: token_type | None = None,
    ) -> tuple[SpotifyOAuth, MemoryCacheHandler]:
        """
        Creates an OAuth handler for Spotify as well as a reference
        to the cache handler

        Parameters
        ----------
        token_info : token_type | None, default=None
            The token information to load into the cache handler

        Returns
        -------
        tuple[spotipy.oauth2.SpotifyOAuth, MemoryCacheHandler]
            The SpotifyOAuth object and the MemoryCacheHandler object
        """
        cache_handler = MemoryCacheHandler(token_info=token_info)

        return (
            SpotifyOAuth(
                cache_handler=cache_handler,
                scope=SpotifyHandler.user_scope,
                redirect_uri=SecretsHandler.get_spotify_redirect_uri(),
                open_browser=False,
                client_id=SecretsHandler.get_spotify_client_id(),
                client_secret=SecretsHandler.get_spotify_client_secret(),
            ),
            cache_handler,
        )

    @staticmethod
    def generate_oauth_url():
        """
        Generates the URL to authenticate a user with Spotify

        Returns
        -------
        str
            The URL to authenticate a user with Spotify and allow
            SentiSounds to access their Spotify account
        """
        OAUTH_URL = "https://accounts.spotify.com/authorize"
        payload = {
            "client_id": SecretsHandler.get_spotify_client_id(),
            "response_type": "code",
            "redirect_uri": SecretsHandler.get_spotify_redirect_uri(),
            "scope": normalize_scope(SpotifyHandler.user_scope),
        }
        return "%s?%s" % (OAUTH_URL, urlencode(payload))

    def get_client(self) -> Spotify:
        """
        Retrieves a Spotify object. This instance can either be
        authenticated with a user or a base client.
        If you would like a user client, use the `SpotifyHandler.from_token`
        classmethod for initialization

        Returns
        -------
        spotipy.Spotify
            The Spotify client instance, either the base client or a user
            client
        """
        return self._client_instance or SpotifyHandler.BASE_CLIENT

    def ensure_authentication(self) -> bool:
        """
        A passthrough for the Spotify.me field.

        Returns
        -------
        bool
            True if a user client was successfully found, False otherwise
        """
        try:
            self.get_client().me()
        except Exception:
            return False

        return True

    def get_token(self) -> token_type | None:
        """
        Gets the token from the cache handler if there has been a token loaded

        Returns
        -------
        token_type | None
            The token information if it exists
        """
        if self.cache_handler:
            return self.cache_handler.get_cached_token()

    def get_genre_songs(
        self,
        genres: list[str],
        limit_per_genre: int = 10,
        popularity_threshold: int = 20,
    ) -> list[song_type]:
        """
        Retrieves a list of songs in each genre sourced from the Spotify API.

        Parameters
        ----------
        genres : list[str]
            The list genres to search songs for. Even if provided with one
            genre, a list must be given
        limit_per_genre : int, default=10
            The number of songs to return from each genre
        popularity_threshold : int, default=30
            The minimum popularity score that will be required
            for each returned song

        Returns
        -------
        list[song_type]
            The list of songs from the Spotify API with the following fields:

            | - name: The name of the song
            | - album: The album the song is from
            |   - - external_urls: A URL to the album
            |   - - images: A list of images for the album
            |   - - name: The name of the album
            | - artists: A list of artists for the song
            |   - - external_urls: A URL to the artist
            |   - - name: The name of the artist
            | - preview_url: A URL to a 30-second preview of the song
            | - external_urls: A URL to the song in different contexts
            | - explicit: Whether the song is explicit
            | - is_playable: Whether the song is playable
            | - popularity: The popularity of the song
            | - id: The ID of the song (useful for creating a playlist)
            | - liked_by_user: Whether the user has liked the song.
                default=False if a user has not been authenticated.
        """
        song_keys_to_extract = [
            "name",
            "album",
            "artists",
            "preview_url",
            "external_urls",
            "explicit",
            "is_playable",
            "popularity",
            "id",
        ]
        album_keys_to_extract = ["name", "images", "external_urls"]
        artist_keys_to_extract = ["name", "external_urls"]

        client_instance = self.get_client()

        all_song_info: list[song_type] = []
        for genre in genres:
            # generate a random number to use as the offset
            random_offset = random.randint(0, 500)
            # A page of results for this genre
            search_result = client_instance.search(
                q="genre:" + genre,
                type="track",
                offset=random_offset,
                market="from_token",
            )
            if not search_result or not search_result["tracks"]["items"]:
                continue

            # Keep filling this genre's list until there are no more results
            # or we run out of space
            genre_song_list: list[song_type] = []
            while len(genre_song_list) < limit_per_genre:
                genre_song_list += [
                    song
                    for song in search_result["tracks"]["items"]
                    if song["popularity"] > popularity_threshold
                ]
                try:
                    search_result = client_instance.next(search_result)
                    assert search_result and search_result["tracks"]
                except Exception:
                    # if the request is at the end of the
                    # list KeyError will be ignored
                    break  # Continue to the next genre

            all_song_info += genre_song_list

        if not all_song_info:
            raise ValueError(
                "Something went wrong searching for songs from Spotify"
            )

        # Only store the information we want to store
        requested_song_info: list[song_type] = [
            {key: song[key] for key in song_keys_to_extract}
            for song in all_song_info
        ]  # type: ignore

        # Only store the album and artist info that we want to store
        for song in requested_song_info:
            song["album"] = {
                key: song["album"][key] for key in album_keys_to_extract
            }
            song["artists"] = [
                {key: artist[key] for key in artist_keys_to_extract}
                for artist in song["artists"]
            ]

        [x.update({"liked_by_user": False}) for x in requested_song_info]

        # Store whether or not the user has liked this song in the past
        if self._client_instance:
            liked_songs = (
                self._client_instance.current_user_saved_tracks_contains(
                    [x.get("id") for x in requested_song_info]
                )
            )

            if liked_songs:
                for song in zip(requested_song_info, liked_songs):
                    song[0]["liked_by_user"] = song[1]

        return requested_song_info

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
        self, playlist_name: str, description: str, song_ids: list[str]
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
        song_ids : list[str]
            A list of song IDs to include in the playlist

        Returns
        -------
        str
            A URL to the created playlist
        """
        if not self._client_instance:
            raise ValueError(
                "A playlist cannot be created via a base (non-user) client."
            )

        client_instance = self._client_instance

        if not (user := client_instance.me()):
            raise ValueError(
                "Something went wrong validating this user's existence"
            )

        playlist = client_instance.user_playlist_create(
            user["id"], playlist_name, public=False, description=description
        )

        if not playlist:
            raise RuntimeError("Something went wrong creating this playlist")

        client_instance.user_playlist_add_tracks(
            user["id"], playlist["id"], song_ids
        )

        return playlist["external_urls"]["spotify"]

    def like_song(self, song_id: str) -> None:
        """
        Likes a song on Spotify.

        Parameters
        ----------
        song_id : str
            The ID of the song to like
        """
        if not self._client_instance:
            raise ValueError(
                "A song cannot be liked via a base (non-user) client."
            )
        self._client_instance.current_user_saved_tracks_add([song_id])

    def unlike_song(self, song_id: str) -> None:
        """
        Un-likes a song on Spotify.

        Parameters
        ----------
        song_id : str
            The ID of the song to unlike
        """
        if not self._client_instance:
            raise ValueError(
                "A song cannot be un-liked via a base (non-user) client."
            )
        self._client_instance.current_user_saved_tracks_delete([song_id])

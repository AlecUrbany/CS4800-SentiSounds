from __future__ import annotations

import random
from typing import Any

from secrets_handler import SecretsHandler
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth


class SpotifyHandler:
    """
    A class to handle all Spotify API interactions.

    There are two types of Spotify clients; a base client and a user client.
    A base client uses the default SentiSounds Spotify account to perform
    Spotify operations. The user client will be able to return results and
    recommendations directly via the Spotify API.

    The `from_base_client` or `from_user_client` classmethods are the easiest
    ways to get a SpotifyHandler instance
    """

    def __init__(self) -> None:
        """
        Initializes a SpotifyHandler instance. This instance gives you full
        control of how to initialize and use the handler. However,
        this comes at the cost of the comfort and abstraction capabilities
        provided by this class.

        Consider using the `from_base_client()` or `from_user_client()`
        classmethods to retrieve the type of handler that you are expecting
        """
        self._client_instance: Spotify | None = None
        self.is_user_client: bool = False

    @classmethod
    def from_base_client(cls: type[SpotifyHandler]) -> SpotifyHandler:
        """Creates a SpotifyHandler initialized with a base client"""
        s = SpotifyHandler()
        s.get_base_client()
        return s

    @classmethod
    def from_user_client(cls: type[SpotifyHandler]) -> SpotifyHandler:
        """Creates a SpotifyHandler initialized with a user client"""
        s = SpotifyHandler()
        s.get_user_client()
        return s

    def get_any_client(self) -> Spotify:
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
        if self.is_user_client:
            return self.get_user_client()
        else:
            return self.get_base_client()

    def get_base_client(self) -> Spotify:
        """
        Retrieves or creates the Spotify client instance with
        no user credentials

        Returns
        -------
        Spotify
            The static Spotify client
        """
        if self._client_instance:
            if self.is_user_client:
                raise RuntimeError(
                    "This instance is a user client, not a base client"
                )

            return self._client_instance

        return self._initialize_base_client()

    def _initialize_base_client(self) -> Spotify:
        """
        Initializes the Spotify client with no user credentials.

        This function should never be called outside of this class. To retrieve
        the client safely, use the `get_base_client` function.

        Returns
        -------
        Spotify
            The base (non-user) Spotify client
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
        Retrieves or creates a Spotify client instance with user credentials

        Returns
        -------
        Spotify
            The authenticated Spotify client
        """

        if self._client_instance:
            if not self.is_user_client:
                raise RuntimeError(
                    "This instance is a base client, not a user client"
                )

            return self._client_instance

        return self._initialize_user_client()

    def _initialize_user_client(self) -> Spotify:
        """
        Initializes the Spotify client with user credentials.

        This function should never be called outside of this class. To retrieve
        the client safely, use the `get_user_client` function.

        Returns
        -------
        Spotify
            The static Spotify client with user credentials
        """
        redirect_uri = "https://github.com/AlecUrbany/CS4800-SentiSounds"
        scope = [
            "streaming",
            "playlist-modify-private",
            "user-top-read",
            "user-read-private"
        ]
        self.is_user_client = True
        self._client_instance = Spotify(
            auth_manager=SpotifyOAuth(
                scope=scope,
                redirect_uri=redirect_uri,
                # TODO: Figure out bypass for redirect URI paste
                open_browser=True,
                client_id=SecretsHandler.get_spotify_client_id(),
                client_secret=SecretsHandler.get_spotify_client_secret()
            )
        )

        return self._client_instance

    def get_genre_songs(
                self,
                genre: str,
                market: str = "from_token",
                limit: int = 10
            ) -> list[dict[str, str | bool | int]]:
        """
        Retrieves a pseudo-random list of songs in a genre sourced from the
        Spotify API.

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
        list[dict[str, str | bool | int]]
            A list of songs retrieved from the Spotify API with the following:
            - name: The name of the song (str)
            - preview_url: A URL to a 30-second preview of the song (str)
            - uri: A URI to the song (str)
            - explicit: Whether the song is explicit (bool)
            - is_playable: Whether the song is playable (bool)
            - popularity: The popularity of the song (int)
            - id: The ID of the song (useful for creating a playlist) (str)
        """
        random_offset = random.randint(0, 1000)
        keys_to_extract = [
            "name",
            "preview_url",
            "uri",
            "explicit",
            "is_playable",
            "popularity",
            "id"
        ]

        client_instance = self.get_any_client()
        search_result = client_instance.search(
            q='genre:' + genre,
            type="track",
            market=market, offset=random_offset, limit=limit
        )

        if not search_result:
            raise ValueError(
                "Something went wrong searching for songs from Spotify"
            )

        tracks_all: list[dict[str, Any]] = search_result["tracks"]["items"]

        return [
            {key: track[key] for key in keys_to_extract}
            for track in tracks_all
        ]

    def get_available_genre_seeds(self) -> list[str]:
        """
        Retrieves a list of available genre "seeds" from the Spotify API.

        Returns
        -------
        list[str]
            The list of available genre seeds
        """
        client_instance = self.get_any_client()

        seeds_result = client_instance.recommendation_genre_seeds()

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
        song_ids : list[str]
            A list of song IDs to include in the playlist

        Returns
        -------
        str
            A URL to the created playlist
        """
        if not self.is_user_client:
            raise ValueError(
                "A playlist cannot be created via a base (non-user) client."
            )

        client_instance = self.get_user_client()

        if not (user := client_instance.me()):
            raise ValueError(
                "Something went wrong validating this user's existence"
            )

        playlist = client_instance.user_playlist_create(
            user["id"],
            playlist_name,
            public=False,
            description=description
        )

        if not playlist:
            raise RuntimeError("Something went wrong creating this playlist")

        client_instance.user_playlist_add_tracks(
            user["id"], playlist["id"], song_ids
        )

        return playlist["external_urls"]["spotify"]

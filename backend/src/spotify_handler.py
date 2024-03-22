from typing import Self
from spotipy import Spotify, CacheHandler
from spotipy.oauth2 import SpotifyOAuth
from secrets_handler import SecretsHandler
from spotify_cache_handlers import *
from urllib.parse import urlencode
from spotipy.util import normalize_scope
import threading

class SpotifyHandler:
    """
    A class to handle all Spotify API interactions.

    Class Attributes
    ----------
    BASE_CLIENT : Spotify
        The base Spotify client instance. This instance is not authenticated with a paticular user
    user_scope : list[str]
        The list of scopes required to access user data

    Attributes
    ----------
    _client_instance : Spotify
        The Spotify client instance, should not be accessed directly
    cache_handler : CacheHandler
        The object getting and storing the Spotify authentication token. It is
        exposed here for direct control of the tokens outside of this object

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
        "user-read-private",
        "user-library-modify",
        "user-library-read"
    ]

    def __init__(self) -> None:
        self._client_instance: Spotify | None = None
        self.cache_handler = None

    @staticmethod
    def create_OAuth(token_info: dict = None) -> tuple[SpotifyOAuth, CacheHandler]:
        """
        Creates an OAuth handler for Spotify as well as a reference to the cache handler

        Parameters
        ----------
        token_info : dict
            The token information to load into the cache handler. Default is None

        Returns
        -------
        tuple[SpotifyOAuth, CacheHandler]
            The SpotifyOAuth object and the CacheHandler object
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
        """
        Generates the URL to authenticate a user with Spotify

        Returns
        -------
        str
            The URL to authenticate a user with Spotify and allow SentiSounds to access their data
        """
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
        Retrieves a Spotify object. This instance can either be
        authenticated with a user or a base client. If you would like a user client,
        use the `load_token` function first.

        Returns
        -------
        Spotify
            The Spotify client instance, either the base client or a user client
        """
        if self._client_instance:
            return self._client_instance
        return SpotifyHandler.BASE_CLIENT


    def load_token(self, token_info) -> Self:
        """
        Initializes the Spotify client with user credentials.

        This function should never be called outside of this class. To retrieve
        the client safely, use the `get_user_client` function.

        Parameters
        ----------
        token_info : dict
            The token information to load into the cache handler

        Returns
        -------
        Self
            The SpotifyHandler object
        """
        auth_manager, self.cache_handler = SpotifyHandler.create_OAuth(token_info=token_info)
        self._client_instance = Spotify(
            auth_manager= auth_manager
        )
        return self

    def get_token(self) -> dict | None:
        """
        Gets the token from the cache handler if there has been a token loaded

        Returns
        -------
        dict | None
            The token information if it exists, otherwise None
        """
        if self.cache_handler is None:
            return None
        else:
            return self.cache_handler.get_cached_token()
        
    def get_liked_songs(self) -> list[dict]:
        """
        Retrieves all the user's liked songs from Spotify

        Returns
        -------
        list[dict]
            A list of the user's liked songs from the Spotify API
        """
        if self._client_instance is None:
            raise Exception(
                "No user has been loaded into the Spotify client instance."
            )
        results = self._client_instance.current_user_saved_tracks(limit=50)
        liked_songs = results["items"]
        try:
            # Get all liked songs by paging through the results of user_saved_tracks
            while results["next"]:
                results = self._client_instance.next(results)
                liked_songs += results["items"]
        except Exception as e:
            print(e)
        return liked_songs

    def get_genre_songs(
                self,
                genres: list[str],
                limit_per_genre: int = 10,
                popularity_threshold: int = 30
            ) -> list[dict]:
        """
        Retrieves a list of songs in each genre sourced from the Spotify API.

        Parameters
        ----------
        genre : list[str]
            The list genres to search songs for.
        limit_per_genre : int
            The number of songs to return from each genre. Default is 10.
        popularity_threshold : int
            The minimum popularity score that will be required by each returned song. Default is 30.

        This list may be user specific, so use the get_available_genre_seeds
        to find user genres

        Returns
        -------
        list[dict]
            The list of songs from the Spotify API with the following:
            - name: The name of the song
            - album: The album the song is from
                - external_urls: A URL to the album
                - images: A list of images for the album
                - name: The name of the album
            - artists: A list of artists for the song
                - external_urls: A URL to the artist
                - name: The name of the artist
            - preview_url: A URL to a 30-second preview of the song
            - external_urls: A URL to the song
            - explicit: Whether the song is explicit
            - is_playable: Whether the song is playable
            - popularity: The popularity of the song
            - id: The ID of the song (useful for creating a playlist)
            - liked_by_user: Whether the user has liked the song
        """
        assert type(genres) == list, "Genres must be a list of strings, even a single genre"
        song_keys_to_extract = [
            "name",
            "album",
            "artists",
            "preview_url",
            "external_urls",
            "explicit",
            "is_playable",
            "popularity",
            "id"
        ]
        album_keys_to_extract = [
            "name",
            "images",
            "external_urls"
        ]
        artist_keys_to_extract = [
            "name",
            "external_urls"
        ]
        # Start collecting liked songs in a separate thread
        if self._client_instance is not None:
            thread = ThreadWithReturnValue(target=self.get_liked_songs)
            thread.start() # TODO This takes 30s - 1m for over 2500 liked songs, maybe we can find a way to cache it on login

        # Collect songs above popularity score from each genre
        song_list = []
        for genre in genres: # This is a list of genres
            results = self.get_client().search(
                q='genre:' + genre,
                type="track",
                market="from_token"
            )["tracks"]
            genre_song_list = []
            try:
                while len(genre_song_list) < limit_per_genre:
                    # Add songs to this list if they are
                    genre_song_list += [song for song in results["items"] 
                                        if song["popularity"] > popularity_threshold]
                    results = self.get_client().next(results)["tracks"] # page the next set of results
            except Exception as e:
                print(str(e) + " of type: " + str(type(e)))
            song_list += genre_song_list
        
        if len(song_list) == 0:
            raise ValueError(
                "Something went wrong searching for songs from Spotify"
            )
        # Prune the list of songs to only include the necessary info
        pruned_songs = [
            {key: track[key] for key in song_keys_to_extract} for track in song_list
        ]
        # Prune the album and artist info
        for song in pruned_songs:
            song["album"] = {key: song["album"][key] for key in album_keys_to_extract}
            song["artists"] = [{key: artist[key] for key in artist_keys_to_extract} for artist in song["artists"]]

        # if the user has liked a song in the found list, add it as a key value pair to the list
        if self._client_instance is not None:
            liked_songs = thread.join()
            liked_songs = [song["track"]["id"] for song in liked_songs]
            for song in pruned_songs:
                song["liked_by_user"] = bool(song["id"] in liked_songs)
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

        
        if self._client_instance is None:
            raise Exception(
                "No user has been loaded into the Spotify client instance."
            )
        
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
    
    def like_song(self, song_id: str) -> None:
        """
        Likes a song on Spotify.

        Parameters
        ----------
        song_id : str
            The ID of the song to like
        """
        if self._client_instance is None:
            raise Exception(
                "No user has been loaded into the Spotify client instance."
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
        if self._client_instance is None:
            raise Exception(
                "No user has been loaded into the Spotify client instance."
            )
        self._client_instance.current_user_saved_tracks_delete([song_id])
class ThreadWithReturnValue(threading.Thread):
    """
    A thread that returns a value when joined for internal use in the SpotifyHandler class
    """

    def __init__(self, group=None, target=None, name=None,
                args=(), kwargs={}, Verbose=None):
        threading.Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self, *args):
        threading.Thread.join(self, *args)
        return self._return



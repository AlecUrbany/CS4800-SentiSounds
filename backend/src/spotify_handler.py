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

    def get_base_client(self) -> Spotify:
        """
        Retrieves or creates the Spotify client instance with no user credentials

        Returns
        -------
        Spotify
            The static Spotify client
        """
        if self._client_instance:
            return self._client_instance

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
            return self._client_instance

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

    
    def get_genre_songs(self, genre: str, market: str, limit: int=10) -> list[dict]:
        """
        Retrieves a pseudo-random list of songs in a genre sourced from the Spotify API.

        Possible genres:
        ['acoustic', 'afrobeat', 'alt-rock', 'alternative', 'ambient', 'anime', 'black-metal',
        'bluegrass', 'blues', 'bossanova', 'brazil', 'breakbeat', 'british', 'cantopop', 'chicago-house', 
        'children', 'chill', 'classical', 'club', 'comedy', 'country', 'dance', 'dancehall', 'death-metal', 
        'deep-house', 'detroit-techno', 'disco', 'disney', 'drum-and-bass', 'dub', 'dubstep', 'edm', 'electro', 
        'electronic', 'emo', 'folk', 'forro', 'french', 'funk', 'garage', 'german', 'gospel', 'goth', 'grindcore', 
        'groove', 'grunge', 'guitar', 'happy', 'hard-rock', 'hardcore', 'hardstyle', 'heavy-metal', 'hip-hop',
        'holidays', 'honky-tonk', 'house', 'idm', 'indian', 'indie', 'indie-pop', 'industrial', 'iranian', 'j-dance', 
        'j-idol', 'j-pop', 'j-rock', 'jazz', 'k-pop', 'kids', 'latin', 'latino', 'malay', 'mandopop', 'metal', 
        'metal-misc', 'metalcore', 'minimal-techno', 'movies', 'mpb', 'new-age', 'new-release', 'opera', 'pagode',
        'party', 'philippines-opm', 'piano', 'pop', 'pop-film', 'post-dubstep', 'power-pop', 'progressive-house', 
        'psych-rock', 'punk', 'punk-rock', 'r-n-b', 'rainy-day', 'reggae', 'reggaeton', 'road-trip', 'rock', 
        'rock-n-roll', 'rockabilly', 'romance', 'sad', 'salsa', 'samba', 'sertanejo', 'show-tunes', 'singer-songwriter', 
        'ska', 'sleep', 'songwriter', 'soul', 'soundtracks', 'spanish', 'study', 'summer', 'swedish', 'synth-pop', 
        'tango', 'techno', 'trance', 'trip-hop', 'turkish', 'work-out', 'world-music']

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
        """
        random_offset = random.randint(0, 1000)
        keys_to_extract = ["name", "preview_url", "uri", "explicit", "is_playable", "popularity"]
        tracks_all = self._client_instance.search(q='genre:' + genre, type="track", market=market, offset=random_offset, limit=limit)["tracks"]["items"]
        return [{key: track[key] for key in keys_to_extract} for track in tracks_all]
    
    def get_available_genre_seeds(self) -> list[str]:
        """
        Retrieves a list of available genre seeds from the Spotify API.

        Returns
        -------
        list[str]
            The list of available genre seeds
        """
        return self._client_instance.recommendation_genre_seeds()["genres"]
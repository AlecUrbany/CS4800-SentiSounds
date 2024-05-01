"""The callable API functions to be used to communicate with the backend"""

import asyncio
import logging
from functools import partial
from typing import Any, Callable

from auth_handler import AuthHandler
from database_handler import DatabaseHandler
from openai_handler import OpenAIHandler
from quart import Quart, request
from quart_cors import cors
from senti_types import song_type, token_type
from spotify_handler import SpotifyHandler
from youtube_handler import YoutubeHandler

app = Quart(__name__)
"""The Quart app to run"""
app = cors(app, allow_origin="https://alecurbany.github.io/CS4800-SentiSounds/")
app.logger.setLevel(logging.INFO)


CLEAN_FREQUENCY = 30
"""How often to clean out the authentication storage in minutes"""


async def routine_clean():
    """
    Routinely cleans out the authentication cache and database.
    """

    while True:
        app.logger.info("Performing routine authentication cleaning.")
        cache_d, db_d = await AuthHandler.clean_authentication()
        app.logger.info(f"Cleared {cache_d} cache items and {db_d} DB items.")
        await asyncio.sleep(CLEAN_FREQUENCY * 60)


@app.before_serving
async def startup():
    """
    Defines start-up functions for the API. Involves setting up the repeating
    background task of cleaning the DB and cache, and initializing the DB pool.
    """

    await DatabaseHandler.get_pool()
    app.add_background_task(routine_clean)


@app.route("/sign-up", methods=["POST"])
async def sign_up():
    """
    `POST /sign-up`

    Sends an authentication email to the given user and checks the validity
    of the given user data

    Parameters must be given in the **body of the API call as form-data**. The
    keys of the data given must be spelled exactly as displayed in the
    parameters list

    Parameters
    ----------
    email_address : str, default=""
        The email address to send the code to
    password : str, default=""
        The password to eventually store for the user
    first_name : str, default=""
        The first name of the user
    last_initial: str, default=""
        The last initial of the user (this will be used with the first name
        to create a display name)

    Returns
    -------
    tuple[dict[str, str], int]
        dict[str, str] is a dictionary denoting the `status` of the operation
        (either success or failure), and an `error` if an error occurred.
        int is 400 if an error occurred and 200 if the operation was
        successful
    """

    passed = await request.form
    try:
        await AuthHandler.sign_up(
            email_address=passed.get("email_address", default=""),
            password=passed.get("password", default=""),
            first_name=passed.get("first_name", default=""),
            last_initial=passed.get("last_initial", default=""),
        )
    except Exception as e:
        return {"status": "failure", "error": str(e)}, 400

    return {"status": "success"}, 200


@app.route("/authenticate", methods=["POST"])
async def authenticate():
    """
    `POST /authenticate`

    Validates a user's email and properly adds them to the database. This
    should be called *after* `/sign-up` has been called, since it requires
    the authentication code receieved via the user's email

    Parameters must be given in the **body of the API call as form-data**. The
    keys of the data given must be spelled exactly as displayed in the
    parameters list

    Parameters
    ----------
    email_address : str, default=""
        The email address to store for the user
    entered_auth : str, default=""
        The authentication code entered by the user

    Returns
    -------
    tuple[dict[str, str], int]
        dict[str, str] is a dictionary denoting the `status` of the operation
        (either success or failure), and an `error` if an error occurred.
        int is 400 if an error occurred and 200 if the operation was
        successful
    """

    await DatabaseHandler.get_pool()

    passed = await request.form
    try:
        await AuthHandler.authenticate_user(
            email_address=passed.get("email_address", default=""),
            entered_auth_code=passed.get("entered_auth_code", default=""),
        )
    except Exception as e:
        return {"status": "failure", "error": str(e)}, 400

    return {"status": "success"}, 200


@app.route("/login", methods=["POST"])
async def login():
    """
    `POST /login`

    Checks whether or not a correct email-address and password pair was passed.
    This essentially ensures that a user logging in has logged in with the
    proper credentials

    Parameters must be given in the **body of the API call as form-data**. The
    keys of the data given must be spelled exactly as displayed in the
    parameters list

    Parameters
    ----------
    email_address : str, default=""
        The email address to check
    password : str, default=""
        The password to check

    Returns
    -------
    tuple[dict[str, str], int]
        dict[str, str] is a dictionary denoting the `status` of the operation
        (either success or failure), and an `error` if an error occurred.
        int is 401 if an incorrect pair was passed and 200 if the operation was
        successful
    """

    await DatabaseHandler.get_pool()

    passed = await request.form
    result = await AuthHandler.log_in(
        email_address=passed.get("email_address", default=""),
        password=passed.get("password", default=""),
    )

    return (
        ({"status": "success"}, 200)
        if result
        else (
            {
                "status": "failure",
                "error": "Incorrect credentials, or that user does not exist."
            },
            401,
        )
    )


@app.route("/spotify-auth-link", methods=["GET"])
def spotify_get_auth_link():
    """
    `GET /spotify-auth-link`

    Retrieves a link to be used to authenticate with Spotify. After the user
    authenticates, they will be redirected to a URL with a code=... parameter.
    This code will need to be passed to `POST spotify-authenticate` to complete
    authentication

    Returns
    -------
    tuple[dict[str, str], int]
        dict[str, str] is a dictionary denoting the `status` of the operation
        (either success or failure), and an `error` if an error occurred.
        int is 400 if an error occurred and 200 if the operation was
        successful
    """

    try:
        return {
            "status": "success",
            "url": SpotifyHandler.generate_oauth_url(),
        }, 200
    except Exception as e:
        return {"status": "failure", "error": str(e)}, 400


@app.route("/spotify-authenticate", methods=["POST"])
async def spotify_authenticate():
    """
    `POST /spotify-authenticate`

    Attempts to authenticate a user with their Spotify account given
    an email address and the 'code' token. To retrieve this code,
    the user must first be redirected to the URL retrieved from
    `GET /spotify-auth-link`.

    Parameters must be given in the **body of the API call as form-data**. The
    keys of the data given must be spelled exactly as displayed in the
    parameters list

    Parameters
    ----------
    email_address : str, default=""
        The email address to check
    code : str, default=""
        The code to use for token retrieval

    Returns
    -------
    tuple[dict[str, str], int]
        dict[str, str] is a dictionary denoting the `status` of the operation
        (either success or failure), and an `error` if an error occurred.
        int is 400 if an error occurred and 200 if the operation was
        successful
    """
    await DatabaseHandler.get_pool()

    passed = await request.form
    email_address = passed.get("email_address", default="")
    code = passed.get("code", default="")

    try:
        if not email_address:
            raise ValueError("No email address was entered")

        if not code:
            raise ValueError("No Spotify authentiction code was entered")

        sp, _ = SpotifyHandler.create_oauth()
        token: token_type = sp.get_access_token(
            code, as_dict=True
        )  # type: ignore
        aff: int = await AuthHandler.save_spotify_token(email_address, token)

        if not aff:
            raise ValueError("No authenticated users found by that email.")

    except Exception as e:
        return {"status": "failure", "error": str(e)}, 400

    return {"status": "success"}, 200


@app.route("/recommend-songs", methods=["POST"])
async def recommend_songs():
    """
    `POST /recommend-songs`

    Given a user's sentiment-littered prompt, return a list of matching
    songs recommended by Spotify

    The prompt must be passed as a URL parameter to the API call, but the
    email address must be passed as a body argument (similar to the
    authentication endpoints). Again, ensure the spelling of the arguments

    Parameters
    ----------
    entered_prompt : str, default=""
        The prompt entered by the user. This should be sanitized, and an error
        will occur if it is not
    email_address : str, default=""
        An optional email address. If it is provided, we attempt to return a
        personalized list of songs to the user based on their Spotify activity
        (Note: this requires that the user has previously linked their
        Spotify account)
    popularity_score: int, default=20
        The popularity score of the songs to retrieve. The lower the score,
        the more... 'special'... songs you'll get. The default (20) strikes
        a fine balance, but this can be adjusted.

    Returns
    -------
    tuple[dict[str, str], int]
        dict[str, str] is a dictionary denoting the `status` of the operation
        (either success or failure), and an `error` if an error occurred.
        We also pass a `songs` field to successful operations containing
        the songs recommended by Spotify
        int is 400 if an error occurred and 200 if the operation was
        successful
    """

    await DatabaseHandler.get_pool()

    passed = await request.form
    email_address = passed.get("email_address", default="")

    entered_prompt = request.args.get("entered_prompt", default="")
    popularity_score = request.args.get(
        "popularity_score",
        default=20,
        type=int,
    )

    try:
        entered_prompt = OpenAIHandler.sanitize_input(entered_prompt)

        found_genres = OpenAIHandler.get_genres(entered_prompt)
        songs: list[song_type] = await uses_token(
            email_address,
            False,
            SpotifyHandler.get_genre_songs,
            found_genres,
            popularity_threshold=popularity_score,
        )  # type: ignore

        YoutubeHandler.match_list(songs)
        YoutubeHandler.save_cache()

    except Exception as e:
        return {"status": "failure", "error": str(e)}, 400
    return {"status": "success", "songs": songs}, 200


@app.route("/export-playlist", methods=["POST"])
async def export_playlist():
    """
    `POST /export-playlist`

    Exports a playlist of song IDs to a user's connected Spotify account

    Though `playlist_name` and playlist_description` are provided as possible
    values, the name should be left to default to "SentiSounds Export", and
    the `entered_prompt` from `api.recommend_songs` should be passed to
    `playlist_description`. These are not hard-constraints, however, and any
    value can be entered.

    The song IDs must be passed as a URL parameter to the API call, but the
    email address must be passed as a body argument (similar to the
    authentication endpoints). Again, ensure the spelling of the arguments

    Parameters
    ----------
    email_address : str, default=""
        The email address of the Spotify account to export the playlist to
    song_ids : str, default=""
        The songs to save in this playlist. This will be a space-separated
        string of songs ex: "123 123 123"
    playlist_name : str, default="SentiSounds Export"
        The name to assign the playlist. By default, we provide a SentiSounds
        branded name
    playlist_description : str, default=""
        The description to assign the playlist. This *should* be the prompt
        that the user originally entered, but any value is fine.

    Returns
    -------
    tuple[dict[str, str], int]
        dict[str, str] is a dictionary denoting the `status` of the operation
        (either success or failure), and an `error` if an error occurred.
        We also pass a `playlist_url` field to successful operations containing
        the link to the playlist we created
        int is 400 if an error occurred and 200 if the operation was
        successful
    """

    await DatabaseHandler.get_pool()

    passed = await request.form
    email_address = passed.get("email_address", default="")

    song_ids = request.args.get("song_ids", default="")
    playlist_name = request.args.get(
        "playlist_name", default="SentiSounds Export"
    )
    playlist_description = request.args.get("playlist_description", default="")
    try:
        created_url: str = await uses_token(
            email_address,
            True,
            SpotifyHandler.create_playlist,
            playlist_name,
            playlist_description,
            song_ids.split(" "),
        )  # type: ignore
    except Exception as e:
        return {"status": "failure", "error": str(e)}, 400

    return {"status": "success", "playlist_url": created_url}, 200


@app.route("/spotify-check-authentication", methods=["POST"])
async def spotify_check_authentication():
    """
    `POST /spotify-check-authentication`

    Checks if a user has authenticated their Spotify account

    Parameters must be given in the **body of the API call as form-data**. The
    keys of the data given must be spelled exactly as displayed in the
    parameters list

    Parameters
    ----------
    email_address : str, default=""
        The email address of the user with an associated Spotify account

    Returns
    -------
    tuple[dict[str, str], int]
        dict[str, str] is a dictionary denoting the `status` of the operation
        (either success or failure), and an `error` if an error occurred.
        int is 400 if an error occurred and 200 if the operation was
        successful
    """
    await DatabaseHandler.get_pool()

    passed = await request.form
    email_address = passed.get("email_address", default="")

    try:
        is_auth = await uses_token(
            email_address, True, SpotifyHandler.ensure_authentication
        )
    except Exception as e:
        return {"status": "failure", "error": str(e)}, 400

    return {"status": "success", "is-authenticated": is_auth}, 200


@app.route("/spotify-like-song", methods=["POST"])
async def spotify_like_song():
    """
    `POST /spotify-like-song`

    Likes a song. If it was already liked, nothing will happen.

    The song ID must be passed as a URL parameter to the API call, but the
    email address must be passed as a body argument (similar to the
    authentication endpoints). Again, ensure the spelling of the arguments

    Parameters
    ----------
    email_address : str, default=""
        The email address of the user whose Spotify account to unlike a song
        from
    song_id: str, default=""
        The song ID of the song to unlike

    Returns
    -------
    tuple[dict[str, str], int]
        dict[str, str] is a dictionary denoting the `status` of the operation
        (either success or failure), and an `error` if an error occurred.
        int is 400 if an error occurred and 200 if the operation was
        successful
    """
    await DatabaseHandler.get_pool()

    passed = await request.form
    email_address = passed.get("email_address", default="")

    song_id = request.args.get("song_id", default="")

    try:
        await uses_token(
            email_address, True, SpotifyHandler.like_song, song_id
        )
    except Exception as e:
        return {"status": "failure", "error": str(e)}, 400

    return {"status": "success"}, 200


@app.route("/spotify-unlike-song", methods=["POST"])
async def spotify_unlike_song():
    """
    `POST /spotify-unlike-song`

    Unlikes a song. If it wasn't already liked, nothing will happen.

    The song ID must be passed as a URL parameter to the API call, but the
    email address must be passed as a body argument (similar to the
    authentication endpoints). Again, ensure the spelling of the arguments

    Parameters
    ----------
    email_address : str, default=""
        The email address of the user whose Spotify account to unlike a song
        from
    song_id: str, default=""
        The song ID of the song to unlike

    Returns
    -------
    tuple[dict[str, str], int]
        dict[str, str] is a dictionary denoting the `status` of the operation
        (either success or failure), and an `error` if an error occurred.
        int is 400 if an error occurred and 200 if the operation was
        successful
    """
    await DatabaseHandler.get_pool()

    passed = await request.form
    email_address = passed.get("email_address", default="")

    song_id = request.args.get("song_id", default="")

    try:
        await uses_token(
            email_address, True, SpotifyHandler.unlike_song, song_id
        )
    except Exception as e:
        return {"status": "failure", "error": str(e)}, 400

    return {"status": "success"}, 200


async def uses_token(
    email_address: str,
    requires_token: bool,
    spotify_function: Callable[..., Any | None],
    *args: Any,
    **kwargs: Any,
) -> Any | None:
    """
    Wraps a call to the Spotify API with token-ensuring functionality

    Parameters
    ----------
    email_address : str
        The email address of the associated Spotify account
    spotify_function : Callable[..., Any | None]
        Any of the SpotifyHandler's functions
    *args : Any
        The arguments to pass to the SpotifyHandler function

    Returns
    -------
    Any | None
        The return value of the function that was called

    Raises
    ------
    ValueError
        If the there is no associated Spotify account for this email address
    """
    token = await AuthHandler.get_spotify_token(email_address)

    if not email_address and requires_token:
        raise ValueError("No email address was entered.")

    if not token and requires_token:
        raise ValueError(
            f"No Spotify account was found for {email_address} in database"
        )

    # By this point, if we *need* the token we are guaranteed to have it
    # If we got to this point, it is safe to *not* have the token and still
    # proceed
    if token:
        sp = SpotifyHandler.from_token(token)
    else:
        sp = SpotifyHandler()

    ret = partial(spotify_function, sp, *args, **kwargs)()

    await AuthHandler.check_and_save_spotify_token(
        email_address, token, sp.get_token()
    )

    return ret

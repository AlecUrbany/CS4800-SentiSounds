"""The callable API functions to be used to communicate with the backend"""

from auth_handler import AuthHandler
from database_handler import DatabaseHandler
from openai_handler import OpenAIHandler
from quart import Quart, request
from spotify_handler import SpotifyHandler

app = Quart(__name__)
"""The Quart app to run"""


@app.route("/sign-up", methods=['POST'])
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
        (either success or failure), and an `error` if an error occured.
        int is 400 if an error occured and 200 if the operation was
        successful
    """
    passed = await request.form
    try:
        AuthHandler.sign_up(
            email_address=passed.get("email_address", default=""),
            password=passed.get("password", default=""),
            first_name=passed.get("first_name", default=""),
            last_initial=passed.get("last_initial", default="")
        )
    except Exception as e:
        return {"status": "failure", "error": str(e)}, 400

    return {"status": "success"}, 200


@app.route("/authenticate", methods=['POST'])
async def authenticate():
    """
    `POST /authenticate`

    Validates a user's email and properly adds them to the database. This
    should be called *after* `/sign-up` has been called, since it requires
    the authentication code receieved via the user's email

    Parameters must be given in the **body of the API call as form-data**. The
    keys of the data given must be spelled exactly as displayed in the
    parameters list

    Although the same parameters passed to `/sign-up` must be passed here,
    `authenticate` will still ensure the validity of the passed parameters

    Parameters
    ----------
    email_address : str, default=""
        The email address to store for the user
    password : str, default=""
        The password to store for the user
    entered_auth : str, default=""
        The authentication code entered by the user
    first_name : str, default=""
        The first name of the user
    last_initial: str, default=""
        The last initial of the user (this will be used with the first name
        to create a display name)

    Returns
    -------
    tuple[dict[str, str], int]
        dict[str, str] is a dictionary denoting the `status` of the operation
        (either success or failure), and an `error` if an error occured.
        int is 400 if an error occured and 200 if the operation was
        successful
    """
    await DatabaseHandler.get_pool()

    passed = await request.form
    try:
        await AuthHandler.authenticate_user(
            email_address=passed.get("email_address", default=""),
            password=passed.get("password", default=""),
            entered_auth_code=passed.get("entered_auth_code", default=""),
            first_name=passed.get("first_name", default=""),
            last_initial=passed.get("last_initial", default="")
        )
    except Exception as e:
        return {"status": "failure", "error": str(e)}, 400

    return {"status": "success"}, 200


@app.route("/login", methods=['POST'])
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
        (either success or failure), and an `error` if an error occured.
        int is 400 if an incorrect pair was passed and 200 if the operation was
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
        if result else
        ({"status": "failure", "error": "Incorrect email or password"}, 401)
    )


@app.route("/spotify-authenticate", methods=['POST'])
async def spotify_authenticate():
    """
    `POST /spotify-authenticate`

    Takes the user through the Spotify authentication process

    **WIP**

    Parameters must be given in the **body of the API call as form-data**. The
    keys of the data given must be spelled exactly as displayed in the
    parameters list

    Return
    ------
    str
        A literal "Hello, World!"
    """
    return "Hello, World!"


@app.route("/recommended-songs", methods=['GET'])
async def recommended_songs():
    """
    `GET /recommended-songs`

    Given a user's sentiment-littered prompt, return a list of matching
    songs recommended by Spotify

    **WIP**

    The prompt must be passed as a header argument to the API call, but the
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

    Return
    ------
    str
        A literal "Hello, World!"
    """
    entered_prompt = request.args.get("prompt", default="")
    email_address = request.args.get("email_address", default="")

    # TODO: Check entered prompt validity
    # TODO: Use email address to create user SpotifyHandler

    try:
        found_genres = OpenAIHandler.get_genres(entered_prompt)
        spotify = SpotifyHandler()

        print(email_address, found_genres)

        spotify.get_genre_songs("")
    except Exception:
        pass

    return "Hello, World!"


@app.route("/export-playlist", methods=['POST'])
async def export_playlist():
    """
    `POST /export-playlist`

    Exports a playlist of song IDs to a user's connected Spotify account

    **WIP**

    Parameters must be given in the **body of the API call as form-data**. The
    keys of the data given must be spelled exactly as displayed in the
    parameters list

    Return
    ------
    str
        A literal "Hello, World!"
    """
    return "Hello, World!"

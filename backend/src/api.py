from quart import Quart, request

from database_handler import DatabaseHandler
from auth_handler import AuthHandler
from openai_handler import OpenAIHandler
from spotify_handler import SpotifyHandler

app = Quart(__name__)

@app.route("/signup", methods=['POST'])
async def sign_up():
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

@app.route("/spotify-get-auth-link", methods=['POST'])
def spotify_get_auth_link():
    """
    Returns a link to authenticate with Spotify
    """
    try:
        return {"status": "success", "url": SpotifyHandler.generate_auth_url()}, 200
    except Exception as e:
        return {"status": "failure", "error": str(e)}, 400

@app.route("/spotify-authenticate", methods=['POST'])
async def spotify_authenticate():
    await DatabaseHandler.get_pool()

    passed = await request.form
    email_address = passed.get("email_address", default="")
    code = passed.get("code", default="")
    try:
        sp = SpotifyHandler.create_OAuth()[0]
        token = sp.get_access_token(code, as_dict=True)
        await AuthHandler.save_spotify_token(email_address, token)
    except Exception as e:
        return {"status": "failure", "error": str(e)}, 400

    return {"status": "success"}, 200

@app.route("/get-songs", methods=['GET'])
async def get_songs():
    entered_prompt = request.args.get("prompt", default="")
    email_address = request.args.get("email_address", default="")

    # TODO: Check entered prompt validity
    # TODO: Use email address to create user SpotifyHandler

    try:
        found_genres = OpenAIHandler.get_genres(entered_prompt)
        spotify = SpotifyHandler(email_address).get_client()
        spotify.get_genre_songs(found_genres)
    except:
        pass


    return "Hello, World!"

@app.route("/export-playlist", methods=['POST'])
async def export_playlist():
    return "Hello, World!"
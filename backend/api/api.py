from flask import Flask

app = Flask(__name__)

@app.route("/signup", methods=['POST'])
def sign_up():
    return "Hello, World!"

@app.route("/authenticate", methods=['POST'])
async def authenticate():
    return "Hello, World!"

@app.route("/login", methods=['POST'])
async def login():
    return "Hello, World!"

@app.route("/spotify-authenticate", methods=['POST'])
async def spotify_authenticate():
    return "Hello, World!"

@app.route("/get-songs", methods=['GET'])
def get_songs():
    return "Hello, World!"

@app.route("/export-playlist", methods=['POST'])
def export_playlist():
    return "Hello, World!"
from api import app
from spotify_handler import SpotifyHandler

if __name__ == "__main__":
    s = SpotifyHandler()
    s.get_user_client()
    print(s.get_genre_songs("rock"))
    app.run()

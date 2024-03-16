"""The main driver for beginning the program's execution"""

from api import app
# from spotify_handler import SpotifyHandler

if __name__ == "__main__":
    # s = SpotifyHandler()
    # s.get_user_client()
    # s.get_genre_songs("rock")
    app.run()

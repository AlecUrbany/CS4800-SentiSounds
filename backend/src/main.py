"""A simple driver for simulating application events"""
from api import app
from spotify_handler import SpotifyHandler

if __name__ == "__main__":
    s = SpotifyHandler()
    s.get_base_client()
    print(s.get_genre_songs("pop"))
    # app.run()
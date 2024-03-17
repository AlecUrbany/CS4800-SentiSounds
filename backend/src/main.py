"""A simple driver for simulating application events"""
from api import app
from spotify_handler import SpotifyHandler

if __name__ == "__main__":
    #s.get_user_client("kjjust7@gmail.com")
    sp = SpotifyHandler("kjjust7@gmail.com")
    sp.get_genre_songs("rock")
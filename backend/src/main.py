"""A simple driver for simulating application events"""

#from openai_handler import OpenAIHandler as ai
from spotify_handler import SpotifyHandler as spotify
from spotipy import SpotifyException


sp = spotify()
#print(ai.get_response("happy"))
sp.get_user_client()
#print(spotify.get_artist("King Gizzard and the Lizard Wizard"))

songs = sp.get_genre_songs("psychedelic rock")
print(songs[3])
ids = [str(x.get("id")) for x in songs]

sp.create_playlist("INSERT MOOD NAME HERE", "WEIRD AND GROOVY", ids)

# > ['pop', 'dance', 'folk', 'reggae', 'disco']
# > ['pop', 'funk', 'disco', 'reggae', 'salsa']
# > ...
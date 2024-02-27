"""A simple driver for simulating application events"""

#from openai_handler import OpenAIHandler as ai
from spotify_handler import SpotifyHandler as spotify


spotify.get_user_client()
#print(ai.get_response("happy"))

#print(spotify.get_artist("King Gizzard and the Lizard Wizard"))
print(spotify.get_genre_songs("alternative", "US", limit=50))
print()
# > ['pop', 'dance', 'folk', 'reggae', 'disco']
# > ['pop', 'funk', 'disco', 'reggae', 'salsa']
# > ...
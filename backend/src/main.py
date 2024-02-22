"""A simple driver for simulating application events"""

from openai_handler import OpenAIHandler as ai

print(ai.get_response("happy"))
# > ['pop', 'dance', 'folk', 'reggae', 'disco']
# > ['Pop', 'Funk', 'Disco', 'Reggae', 'Salsa']
# > ['Pop', 'Funk', 'Dance', 'Reggae', 'Soul']
# > ...
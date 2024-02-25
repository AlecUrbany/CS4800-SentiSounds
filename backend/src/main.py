"""A simple driver for simulating application events"""

from openai_handler import OpenAIHandler as ai

print(ai.get_response("happy"))
# > ['pop', 'dance', 'folk', 'reggae', 'disco']
# > ['pop', 'funk', 'disco', 'reggae', 'salsa']
# > ...
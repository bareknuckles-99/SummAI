# This is a test py app to check if OpenAI api key is being correctly fetched 

from dotenv import load_dotenv
import os

load_dotenv()  # no arguments, loads .env automatically

print("OPENAI_API_KEY:", os.environ.get('OPENAI_API_KEY'))

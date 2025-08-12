from dotenv import load_dotenv
import os

load_dotenv()  # no arguments, loads .env automatically

print("OPENAI_API_KEY:", os.environ.get('OPENAI_API_KEY'))
import os
from dotenv import load_dotenv

load_dotenv()

base_url = os.getenv("API_URL")
key = os.getenv("API_KEY")
id = os.getenv("KNOWLEDGE_BASE_ID")
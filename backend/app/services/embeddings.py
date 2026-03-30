from openai import OpenAI
from dotenv import load_dotenv
import os

# 👇 ADD THIS LINE
load_dotenv()
print("KEY:", os.getenv("OPENAI_API_KEY"))

# 👇 this will now read from .env
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_embedding(text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding
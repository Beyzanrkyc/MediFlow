from openai import OpenAI
from dotenv import load_dotenv
import os

# 👇 ADD THIS
load_dotenv()

print("KEY:", os.getenv("OPENAI_API_KEY"))

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_answer(query, context_chunks):
    context = "\n\n".join(context_chunks)

    prompt = f"""
You are a medical assistant using NHS guidelines.

Context:
{context}

Question:
{query}

Answer clearly and safely:
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content
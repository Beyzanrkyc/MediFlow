from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

USE_LOCAL = False  # set True if using Ollama

if not USE_LOCAL:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_answer(query, context_chunks):
    context = "\n\n".join(context_chunks)

    prompt = f"""
You are a cautious NHS medical assistant.

Rules:
- Do NOT diagnose
- Be safe and conservative
- Recommend professional care if needed

Context:
{context}

User:
{query}

Answer:
"""

    if USE_LOCAL:
        import ollama

        response = ollama.chat(
            model="llama3",
            messages=[{"role": "user", "content": prompt}]
        )
        return response["message"]["content"]

    else:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # ✅ WORKING MODEL
            messages=[{"role": "user", "content": prompt}],
        )

        return response.choices[0].message.content

def stream_answer(query, context_chunks):
    context = "\n\n".join(context_chunks)

    prompt = f"""
You are a cautious NHS medical assistant.

Context:
{context}

User:
{query}

Answer:
"""

    if USE_LOCAL:
        import ollama

        response = ollama.chat(
            model="llama3",
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )

        for chunk in response:
            yield chunk["message"]["content"]

    else:
        try:
            stream = client.chat.completions.create(
                model="llama-3.1-8b-instant",  # ✅ WORKING MODEL
                messages=[{"role": "user", "content": prompt}],
                stream=True
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            print("STREAM ERROR:", str(e))
            yield "⚠️ AI service temporarily unavailable. Please try again."
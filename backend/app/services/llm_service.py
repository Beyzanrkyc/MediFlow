from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

USE_LOCAL = False  # set True if using Ollama

if not USE_LOCAL:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# 🔥 NEW NHS SAFE PROMPT FUNCTION
def build_prompt(query, context):
    return f"""
You are an NHS AI Symptom Checker.

STRICT RULES:
- You are NOT a doctor
- You do NOT provide diagnosis
- You do NOT act like you are physically with the patient
- You do NOT give clinical procedures (NO "I will check", NO "lie down", etc.)
- You ONLY provide general guidance based on NHS advice

YOUR ROLE:
1. Ask relevant follow-up questions about symptoms
2. Assess risk level:
   - LOW: mild symptoms → self-care or GP
   - URGENT: serious symptoms → advise going to A&E
3. Be cautious and safety-focused

STYLE:
- Clear, calm, short
- Simple language
- No hospital roleplay

CONTEXT (NHS GUIDELINES):
{context}

USER INPUT:
{query}

RESPONSE FORMAT:
- Start with a short assessment
- Ask 1–3 follow-up questions
- End with:

Triage Level: LOW or URGENT

ANSWER:
"""


def generate_answer(query, context_chunks):
    context = "\n\n".join(context_chunks)
    prompt = build_prompt(query, context)

    if USE_LOCAL:
        import ollama

        response = ollama.chat(
            model="llama3",
            messages=[{"role": "user", "content": prompt}]
        )
        return response["message"]["content"]

    else:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # ✅ working model
            messages=[{"role": "user", "content": prompt}],
        )

        return response.choices[0].message.content


def stream_answer(query, context_chunks):
    context = "\n\n".join(context_chunks)
    prompt = build_prompt(query, context)

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
                model="llama-3.1-8b-instant",  # ✅ working model
                messages=[{"role": "user", "content": prompt}],
                stream=True
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            print("STREAM ERROR:", str(e))
            yield "⚠️ AI service temporarily unavailable. Please try again."
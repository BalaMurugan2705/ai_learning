import os

from groq import Groq

from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def generate_answer(question, context):

    prompt = f"""
You are a documentation assistant.

Answer the user's question using ONLY the provided documentation.

If the documentation does not contain enough information to answer
the question, say:

"I don't know based on the provided documents."

Do not use outside knowledge.
Do not guess.

USER QUESTION:
{question}

DOCUMENTATION:
{context}
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": "You are a documentation assistant. Answer only from provided documentation.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0,
    )

    return response.choices[0].message.content
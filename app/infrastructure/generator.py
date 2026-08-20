"""AnswerGenerator adapter backed by Groq. All prompt construction and the
Groq client itself are private to this module."""
from groq import Groq


class GroqAnswerGenerator:
    def __init__(self, api_key: str, model: str, temperature: float, refusal_message: str):
        self._client = Groq(api_key=api_key)
        self._model = model
        self._temperature = temperature
        self._refusal_message = refusal_message

    def _build_prompt(self, question: str, context: str) -> str:
        return f"""
You are a documentation assistant.

Answer the user's question using ONLY the provided documentation.

If the documentation does not contain enough information to answer
the question, say:

"{self._refusal_message}"

Do not use outside knowledge.
Do not guess.

USER QUESTION:
{question}

DOCUMENTATION:
{context}
"""

    def generate(self, question: str, context: str) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a documentation assistant. Answer only from provided documentation.",
                },
                {
                    "role": "user",
                    "content": self._build_prompt(question, context),
                },
            ],
            temperature=self._temperature,
        )

        return response.choices[0].message.content

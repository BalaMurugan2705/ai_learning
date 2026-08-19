from generator import generate_answer


answer = generate_answer(
    question="What is the default cache size?",
    context="""
The Acme SDK documentation says:

The retry_backoff_ms parameter defaults to 500 milliseconds.
""",
)


print(answer)
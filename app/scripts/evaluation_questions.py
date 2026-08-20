QUESTIONS = [
    {
        "id": "Q1",
        "question": "What is the default value of retry_backoff_ms?",
        "expected_answer": "500",
        "source_file": "client.md",
        "page_id": "client",
        "section": "Client.send() → Parameters",
    },
    {
        "id": "Q2",
        "question": "What type is the retry_backoff_ms parameter?",
        "expected_answer": "int",
        "source_file": "client.md",
        "page_id": "client",
        "section": "Client.send() → Parameters",
    },
    {
        "id": "Q3",
        "question": "What is the default value of max_retries?",
        "expected_answer": "3",
        "source_file": "client.md",
        "page_id": "client",
        "section": "Client.send() → Parameters",
    },
    {
        "id": "Q4",
        "question": "What value is passed to retry_backoff_ms in the Client.send() example?",
        "expected_answer": "500",
        "source_file": "client.md",
        "page_id": "client",
        "section": "Client.send() → Example",
    },
    {
        "id": "Q5",
        "question": "Is api_key required for Authentication.configure()?",
        "expected_answer": "yes",
        "source_file": "authentication.md",
        "page_id": "authentication",
        "section": "Authentication.configure() → Parameters",
    },
    {
        "id": "Q6",
        "question": "What is the default value of compression in Request.create()?",
        "expected_answer": "true",
        "source_file": "requests.md",
        "page_id": "requests",
        "section": "Request.create() → Parameters",
    },
    {
        "id": "Q7",
        "question": "What is the default page_size for Pagination.configure()?",
        "expected_answer": "50",
        "source_file": "pagination.md",
        "page_id": "pagination",
        "section": "Pagination.configure() → Parameters",
    },
    {
        "id": "Q8",
        "question": "What does the strict parameter control in Response.parse()?",
        "expected_answer": "controls whether malformed response data causes an error",
        "source_file": "responses.md",
        "page_id": "responses",
        "section": "Response.parse() → Parameters",
    },
]

print(f"Number of questions: {len(QUESTIONS)}")

for question in QUESTIONS:
    print(question["id"], "-", question["question"])
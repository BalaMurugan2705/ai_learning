from app.core.dependencies import get_rag_service

rag_service = get_rag_service()


QUESTIONS = [
    {
        "id": "Q1",
        "question": "What is the default value of retry_backoff_ms?",
        "type": "answerable",
    },
    {
        "id": "Q2",
        "question": "What is the default page_size for Pagination.configure()?",
        "type": "answerable",
    },
    {
        "id": "Q3",
        "question": "Is api_key required for Authentication.configure()?",
        "type": "answerable",
    },
    {
        "id": "Q4",
        "question": "What is the default cache size for the Acme SDK?",
        "type": "unanswerable",
    },
    {
        "id": "Q5",
        "question": "What is the maximum number of concurrent requests supported?",
        "type": "unanswerable",
    },
    {
        "id": "Q6",
        "question": "What is the monthly price of the Acme SDK?",
        "type": "unanswerable",
    },
]


for item in QUESTIONS:

    question = item["question"]

    # Goes through the real pipeline (RagService.answer), so the
    # distance-threshold refusal is actually exercised here, not bypassed.
    answer, sources = rag_service.answer(question)

    print("\n" + "=" * 70)
    print(item["id"])
    print("=" * 70)

    print("Type:", item["type"])
    print("Question:", question)
    print("Answer:", answer)

    if sources:
        print("Sources:")
        for source in sources:
            print(
                f"  - chunk_id={source['chunk_id']} "
                f"source_file={source['source_file']} "
                f"section={source['section']!r}"
            )
    else:
        print("Sources: (none — refused)")
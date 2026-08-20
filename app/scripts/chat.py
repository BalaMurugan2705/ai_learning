from app.core.dependencies import get_rag_service

rag_service = get_rag_service()


question = input("Ask a question: ")


answer, sources = rag_service.answer(question)


print("\nANSWER:")
print(answer)


if sources:

    print("\nSOURCES:")

    for index, source in enumerate(sources, start=1):

        print(
            f"[{index}] "
            f"`{source['source_file']}`"
        )

        print(
            f"    Chunk: {source['chunk_id']}"
        )

        print(
            f"    Page: {source['page_id']}"
        )

        print(
            f"    Section: {source['section']}"
        )

else:

    print("\nSOURCES:")
    print("No supporting source found.")
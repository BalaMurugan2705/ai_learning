from rag import answer_question


question = input("Ask a question: ")


answer, sources = answer_question(question)


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
            f"    Page: {source['page_id']}"
        )

        print(
            f"    Section: {source['section']}"
        )

else:

    print("\nSOURCES:")
    print("No supporting source found.")
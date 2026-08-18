from pathlib import Path


def load_document(file_path):
    text = Path(file_path).read_text(encoding="utf-8")
    return text


# document = load_document("data/docs/client.md")

# print(document)
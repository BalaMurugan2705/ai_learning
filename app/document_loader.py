from io import BytesIO

from pypdf import PdfReader


def load_uploaded_document(
    filename,
    content,
):

    extension = filename.rsplit(
        ".",
        1,
    )[-1].lower()


    if extension in {
        "md",
        "txt",
    }:

        return content.decode("utf-8")


    if extension == "pdf":

        reader = PdfReader(
            BytesIO(content)
        )

        pages = []

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:

                pages.append(page_text)


        return "\n\n".join(pages)


    raise ValueError(
        "Unsupported file type"
    )
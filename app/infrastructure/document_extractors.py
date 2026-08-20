"""TextExtractor adapters for each uploadable format, plus a dispatcher.

Adding a new upload format (e.g. .docx) means adding one new extractor to
the list passed into ExtensionBasedTextExtractor — PlainTextExtractor,
PdfTextExtractor, and the dispatcher itself never change (open/closed)."""
from io import BytesIO

from pypdf import PdfReader


class PlainTextExtractor:
    _EXTENSIONS = {"md", "txt"}

    def supports(self, extension: str) -> bool:
        return extension in self._EXTENSIONS

    def extract(self, content: bytes) -> str:
        return content.decode("utf-8")


class PdfTextExtractor:
    _EXTENSIONS = {"pdf"}

    def supports(self, extension: str) -> bool:
        return extension in self._EXTENSIONS

    def extract(self, content: bytes) -> str:
        reader = PdfReader(BytesIO(content))
        pages = [page.extract_text() for page in reader.pages]
        return "\n\n".join(page for page in pages if page)


class ExtensionBasedTextExtractor:
    def __init__(self, extractors: list):
        self._extractors = extractors

    def extract_from_filename(self, filename: str, content: bytes) -> str:
        extension = filename.rsplit(".", 1)[-1].lower()

        for extractor in self._extractors:
            if extractor.supports(extension):
                return extractor.extract(content)

        raise ValueError(f"Unsupported file type: .{extension}")

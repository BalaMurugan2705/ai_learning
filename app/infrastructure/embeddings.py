"""EmbeddingProvider adapter backed by sentence-transformers. Nothing
outside this module (and the composition root that constructs it) knows
sentence-transformers exists."""
from sentence_transformers import SentenceTransformer


class SentenceTransformerEmbeddingProvider:
    def __init__(self, model_name: str):
        self._model = SentenceTransformer(model_name)

    def embed(self, text: str) -> list[float]:
        return self._model.encode(text)

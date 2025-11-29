from sentence_transformers import SentenceTransformer
from ..config import settings

class EmbedderService:
    _model = None

    @classmethod
    def get_model(cls):
        if cls._model is None:
            cls._model = SentenceTransformer(settings.EMBEDDING_MODEL)
        return cls._model

    @classmethod
    def encode(cls, text: str) -> list:
        return cls.get_model().encode(text).tolist()
    
    @classmethod
    def encode_batch(cls, texts: list) -> list:
        return cls.get_model().encode(texts, normalize_embeddings=True, convert_to_numpy=True).tolist()
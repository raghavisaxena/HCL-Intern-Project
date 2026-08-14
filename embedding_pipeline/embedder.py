from sentence_transformers import SentenceTransformer
from loguru import logger

from embedding_pipeline.config import (
    EMBEDDING_MODEL_NAME,
    ENCODE_BATCH_SIZE,
)

QUERY_INSTRUCTION = (
    "Represent this sentence for searching relevant passages: "
)


class TicketEmbedder:

    def __init__(self, model_name: str = EMBEDDING_MODEL_NAME):
        logger.info(
            f"Loading embedding model '{model_name}'..."
        )

        self.model = SentenceTransformer(model_name)

        logger.info("Embedding model loaded.")

    def embed_documents(self, texts: list[str]):
        return self.model.encode(
            texts,
            batch_size=ENCODE_BATCH_SIZE,
            show_progress_bar=True,
            normalize_embeddings=True,
        )

    def embed_query(self, text: str):
        prefixed = QUERY_INSTRUCTION + text

        return self.model.encode(
            [prefixed],
            normalize_embeddings=True,
        )[0]
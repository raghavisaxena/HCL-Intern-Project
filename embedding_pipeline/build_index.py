import pandas as pd
from loguru import logger

from embedding_pipeline.config import PROCESSED_DATA_PATH

from embedding_pipeline.embedder import TicketEmbedder

from embedding_pipeline.vector_store import (
    build_index,
    save_index,
)


def main():

    if not PROCESSED_DATA_PATH.exists():

        raise FileNotFoundError(
            f"Cleaned dataset not found at "
            f"{PROCESSED_DATA_PATH}. "
            "Run the data pipeline first."
        )

    logger.info(
        f"Loading cleaned tickets from "
        f"{PROCESSED_DATA_PATH}"
    )

    df = pd.read_csv(
        PROCESSED_DATA_PATH
    )

    logger.info(
        f"Loaded {len(df):,} tickets"
    )

    embedder = TicketEmbedder()

    texts = df["full_text"].fillna("").tolist()

    embeddings = embedder.embed_documents(
        texts
    )

    logger.info(
        f"Embedding shape: {embeddings.shape}"
    )

    index = build_index(
        embeddings
    )

    metadata = df[
        [
            "ticket_id",
            "subject",
            "description",
            "category",
            "subcategory",
            "priority_raw",
            "resolution",
        ]
    ].copy()

    save_index(
        index,
        metadata
    )

    print(
        f"\n✅ FAISS index built "
        f"for {len(df):,} tickets."
    )


if __name__ == "__main__":
    main()
import faiss
import numpy as np
import pandas as pd
from loguru import logger

from embedding_pipeline.config import (
    FAISS_INDEX_PATH,
    FAISS_METADATA_PATH,
    EMBEDDING_DIMENSION,
    VECTORSTORE_DIR,
)


def build_index(embeddings: np.ndarray) -> faiss.Index:

    if embeddings.shape[1] != EMBEDDING_DIMENSION:
        raise ValueError(
            f"Expected {EMBEDDING_DIMENSION}-dim vectors, "
            f"got {embeddings.shape[1]}"
        )

    index = faiss.IndexFlatIP(EMBEDDING_DIMENSION)

    index.add(embeddings.astype("float32"))

    logger.info(
        f"Built FAISS index with {index.ntotal:,} vectors"
    )

    return index


def save_index(index: faiss.Index, metadata: pd.DataFrame) -> None:

    VECTORSTORE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    faiss.write_index(
        index,
        str(FAISS_INDEX_PATH)
    )

    metadata.to_parquet(
        FAISS_METADATA_PATH,
        index=False
    )

    logger.info(
        f"Saved FAISS index to {FAISS_INDEX_PATH}"
    )

    logger.info(
        f"Saved metadata to {FAISS_METADATA_PATH}"
    )


def load_index():

    if not FAISS_INDEX_PATH.exists():
        raise FileNotFoundError(
            f"No FAISS index found at {FAISS_INDEX_PATH}. "
            "Run build_index first."
        )

    index = faiss.read_index(
        str(FAISS_INDEX_PATH)
    )

    metadata = pd.read_parquet(
        FAISS_METADATA_PATH
    )

    logger.info(
        f"Loaded FAISS index with {index.ntotal:,} vectors"
    )

    return index, metadata


def search(
    index,
    metadata,
    query_vector: np.ndarray,
    top_k: int = 5
):

    query_vector = (
        query_vector
        .astype("float32")
        .reshape(1, -1)
    )

    scores, indices = index.search(
        query_vector,
        top_k
    )

    results = metadata.iloc[
        indices[0]
    ].copy()

    results["similarity_score"] = scores[0]

    return results.reset_index(drop=True)
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROCESSED_DATA_PATH = (
    PROJECT_ROOT / "data" / "processed" / "tickets_clean.csv"
)

VECTORSTORE_DIR = PROJECT_ROOT / "vectorstore"

FAISS_INDEX_PATH = VECTORSTORE_DIR / "tickets.index"

FAISS_METADATA_PATH = (
    VECTORSTORE_DIR / "tickets_metadata.parquet"
)

EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"

EMBEDDING_DIMENSION = 384

ENCODE_BATCH_SIZE = 32
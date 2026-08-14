"""
Centralized file paths for the data pipeline.

Keeping paths in one place means if we ever restructure folders,
we change one file instead of hunting through every script.
"""

from pathlib import Path

# Project root = one level up from this data_pipeline/ folder
PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "tickets_raw.csv"
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "tickets_clean.csv"

TRAIN_SPLIT_PATH = PROJECT_ROOT / "data" / "processed" / "tickets_train.csv"
VAL_SPLIT_PATH = PROJECT_ROOT / "data" / "processed" / "tickets_val.csv"
TEST_SPLIT_PATH = PROJECT_ROOT / "data" / "processed" / "tickets_test.csv"

EDA_OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "eda_report"

# Columns we actually need from the raw Kaggle file.
# The raw file has more columns (business_type, extra tags, etc.) that
# we don't use in this project — we drop them during cleaning.
RAW_COLUMNS_NEEDED = [
    "subject",
    "body",
    "answer",
    "type",
    "queue",
    "priority",
    "language",
    "tag_1",
    "tag_2",
    "tag_3",
]

# Our internal, project-facing schema after cleaning.
# Renaming to these names decouples the rest of our codebase from
# whatever column names Kaggle happens to use.
CLEAN_SCHEMA = {
    "subject": "subject",
    "body": "description",
    "answer": "resolution",
    "type": "ticket_type",
    "queue": "category",       # maps to Assignment Agent's team
    "priority": "priority_raw",  # mapped to P1-P4 later in Phase 9
    "tag_1": "subcategory",
}
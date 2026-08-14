"""
Cleans the raw ticket dataframe into a training-ready dataset.

Each cleaning step is its own small function — this makes the
pipeline easy to test, easy to reorder, and easy to explain (each
function name documents exactly what happens to the data).
"""

import re
import pandas as pd
from loguru import logger

from data_pipeline.config import CLEAN_SCHEMA


def filter_english_only(df: pd.DataFrame) -> pd.DataFrame:
    """
    Keeps only English-language tickets.

    Why: our embedding model (BAAI/bge-small-en-v1.5) and Phi-3 Mini
    prompts in this project are optimized for English. Mixing languages
    now would hurt both classification accuracy and retrieval quality.
    Multilingual support is a reasonable future enhancement, not a v1
    requirement.
    """
    before = len(df)
    df = df[df["language"].str.lower() == "en"].copy()
    logger.info(f"Filtered to English only: {before:,} -> {len(df):,} rows")
    return df


def drop_missing_critical_fields(df: pd.DataFrame) -> pd.DataFrame:
    """
    Drops rows missing any field the project absolutely cannot work
    without: the ticket text itself, its category, priority, and
    resolution. A ticket with no body or no label is useless training
    signal — keeping it would only introduce noise.
    """
    before = len(df)
    critical = ["subject", "body", "answer", "queue", "priority"]
    df = df.dropna(subset=critical).copy()
    logger.info(f"Dropped rows missing critical fields: {before:,} -> {len(df):,} rows")
    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Removes exact duplicate tickets (same subject + body).

    Why: duplicate rows silently bias both classification training
    (that category gets over-weighted) and RAG retrieval (the same
    ticket appears multiple times in "similar incidents" results).
    """
    before = len(df)
    df = df.drop_duplicates(subset=["subject", "body"]).copy()
    logger.info(f"Removed duplicate tickets: {before:,} -> {len(df):,} rows")
    return df


def clean_text(text: str) -> str:
    """
    Normalizes a single text field:
    - collapses excess whitespace/newlines
    - strips leading/trailing whitespace
    - removes common email boilerplate artifacts (signatures, quoted
      reply headers) that add noise without adding meaning
    """
    if not isinstance(text, str):
        return ""

    # Collapse multiple newlines/spaces into single spaces
    text = re.sub(r"\s+", " ", text)

    # Strip common email reply/quote artifacts, e.g. "On Mon, ... wrote:"
    text = re.sub(r"On .{0,60} wrote:.*", "", text)

    # Strip a trailing "Best regards," / "Kind regards," style signature
    text = re.sub(r"(Best regards|Kind regards|Sincerely|Thanks,).*", "", text, flags=re.IGNORECASE)

    return text.strip()


def apply_text_cleaning(df: pd.DataFrame) -> pd.DataFrame:
    """Applies clean_text() to every free-text column."""
    for col in ["subject", "body", "answer"]:
        df[col] = df[col].apply(clean_text)

    # After cleaning, some rows might have become empty — drop those too
    before = len(df)
    df = df[(df["body"].str.len() > 0) & (df["answer"].str.len() > 0)].copy()
    logger.info(f"Dropped rows emptied by text cleaning: {before:,} -> {len(df):,} rows")
    return df


def standardize_priority(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardizes priority values to a consistent lowercase form
    (e.g. " High " -> "high"). We keep the raw low/medium/high scale
    here — the actual mapping to P1-P4 happens in Phase 9, where we
    also fold in impact/urgency reasoning, not just this raw label.
    """
    df["priority"] = df["priority"].astype(str).str.strip().str.lower()
    valid_priorities = {"low", "medium", "high"}
    before = len(df)
    df = df[df["priority"].isin(valid_priorities)].copy()
    logger.info(f"Standardized priority, dropped invalid values: {before:,} -> {len(df):,} rows")
    return df


def standardize_category_fields(df: pd.DataFrame) -> pd.DataFrame:
    """Trims and title-cases the queue (category) and type fields for consistency."""
    df["queue"] = df["queue"].astype(str).str.strip()
    df["type"] = df["type"].astype(str).str.strip()
    df["tag_1"] = df["tag_1"].fillna("General").astype(str).str.strip()
    return df


def add_derived_fields(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds fields our later phases will need:
    - `ticket_id`: a stable synthetic ID (the raw data doesn't have one)
    - `full_text`: subject + body combined, this is what we'll embed
      in Phase 5 (embedding both gives better semantic signal than
      body alone)
    """
    df = df.reset_index(drop=True)
    df["ticket_id"] = ["INC" + str(100000 + i) for i in df.index]
    df["full_text"] = (df["subject"] + ". " + df["body"]).str.strip()
    return df


def rename_to_clean_schema(df: pd.DataFrame) -> pd.DataFrame:
    """Renames raw Kaggle column names to our internal project schema (see config.py)."""
    df = df.rename(columns=CLEAN_SCHEMA)
    return df


def clean_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """
    Runs the full cleaning pipeline in order. Order matters here:
    we filter/dedupe on raw text BEFORE cleaning it (cheaper), and
    only rename columns at the very end so every function above can
    rely on consistent, original Kaggle column names.
    """
    logger.info("Starting cleaning pipeline...")
    df = filter_english_only(df)
    df = drop_missing_critical_fields(df)
    df = remove_duplicates(df)
    df = apply_text_cleaning(df)
    df = standardize_priority(df)
    df = standardize_category_fields(df)
    df = add_derived_fields(df)
    df = rename_to_clean_schema(df)
    logger.info(f"Cleaning complete. Final dataset: {len(df):,} rows")
    return df
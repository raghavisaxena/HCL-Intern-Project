"""
Exploratory Data Analysis (EDA) for the cleaned ticket dataset.

Why EDA matters here specifically:
- Class distribution (category/priority) tells us if some agents will
  need to handle severe class imbalance (e.g., if 90% of tickets are
  "Technical Support", our Classification Agent needs to be evaluated
  carefully, not just judged on raw accuracy).
- Text length distribution informs prompt design later (Phase 7) —
  if descriptions are very long, we need to think about token limits
  when we build Phi-3 Mini prompts.
"""

import matplotlib
matplotlib.use("Agg")  # headless backend — saves files, doesn't try to open a window
import matplotlib.pyplot as plt
import pandas as pd
from loguru import logger

from data_pipeline.config import EDA_OUTPUT_DIR


def run_eda(df: pd.DataFrame) -> dict:
    """
    Computes and prints key statistics, and saves a handful of
    charts to disk. Returns a dict of summary stats in case calling
    code wants to inspect them programmatically (e.g. for a report).
    """
    EDA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("EXPLORATORY DATA ANALYSIS")
    print("=" * 60)

    print(f"\nTotal tickets: {len(df):,}")

    print("\n--- Category (queue) distribution ---")
    category_counts = df["category"].value_counts()
    print(category_counts.to_string())

    print("\n--- Priority distribution ---")
    priority_counts = df["priority_raw"].value_counts()
    print(priority_counts.to_string())

    print("\n--- Ticket type distribution ---")
    type_counts = df["ticket_type"].value_counts()
    print(type_counts.to_string())

    print("\n--- Top 15 subcategories (tag_1) ---")
    subcat_counts = df["subcategory"].value_counts().head(15)
    print(subcat_counts.to_string())

    # Text length stats — informs prompt/token budgeting in Phase 7
    df["description_word_count"] = df["description"].str.split().str.len()
    print("\n--- Description length (words) ---")
    print(df["description_word_count"].describe().to_string())

    # --- Save charts ---
    _save_bar_chart(
        category_counts, "Ticket Count by Category (Queue)",
        EDA_OUTPUT_DIR / "category_distribution.png"
    )
    _save_bar_chart(
        priority_counts, "Ticket Count by Priority",
        EDA_OUTPUT_DIR / "priority_distribution.png"
    )
    _save_histogram(
        df["description_word_count"], "Description Length (word count)",
        EDA_OUTPUT_DIR / "description_length_hist.png"
    )

    logger.info(f"EDA charts saved to {EDA_OUTPUT_DIR}")
    print("=" * 60)

    return {
        "total_tickets": len(df),
        "category_counts": category_counts.to_dict(),
        "priority_counts": priority_counts.to_dict(),
        "type_counts": type_counts.to_dict(),
    }


def _save_bar_chart(series: pd.Series, title: str, output_path) -> None:
    plt.figure(figsize=(8, 5))
    series.plot(kind="bar", color="#2563eb")
    plt.title(title)
    plt.ylabel("Number of Tickets")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=120)
    plt.close()


def _save_histogram(series: pd.Series, title: str, output_path) -> None:
    plt.figure(figsize=(8, 5))
    series.plot(kind="hist", bins=30, color="#16a34a")
    plt.title(title)
    plt.xlabel("Word Count")
    plt.tight_layout()
    plt.savefig(output_path, dpi=120)
    plt.close()
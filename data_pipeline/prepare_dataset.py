"""
Main entrypoint for the data pipeline.

Run with:
    python -m data_pipeline.prepare_dataset

This ties together loading -> cleaning -> EDA -> train/val/test
splitting -> saving, in one reproducible command. Anyone on the team
(or your future self) can regenerate the entire processed dataset
from raw data with a single command.
"""

from loguru import logger

from data_pipeline.config import (
    PROCESSED_DATA_PATH,
    TRAIN_SPLIT_PATH,
    VAL_SPLIT_PATH,
    TEST_SPLIT_PATH,
)
from data_pipeline.load_data import load_raw_data, inspect_raw_data
from data_pipeline.clean_data import clean_pipeline
from data_pipeline.eda import run_eda


def split_train_val_test(df, train_frac=0.8, val_frac=0.1, seed=42):
    """
    Splits the cleaned dataset into train/val/test sets.

    Why we need three sets, not just train/test:
    - train: what the models actually learn from
    - val (validation): used during development to tune prompts/models
      and check we're not overfitting, WITHOUT peeking at test data
    - test: touched only once, at the very end, to report final
      honest performance numbers

    We shuffle with a fixed random seed (42) so the split is
    reproducible - running this script twice gives the same three
    files, which matters for consistent experiments.
    """
    df_shuffled = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)

    n = len(df_shuffled)
    train_end = int(n * train_frac)
    val_end = train_end + int(n * val_frac)

    train_df = df_shuffled.iloc[:train_end]
    val_df = df_shuffled.iloc[train_end:val_end]
    test_df = df_shuffled.iloc[val_end:]

    logger.info(
        f"Split into train={len(train_df):,} / val={len(val_df):,} / test={len(test_df):,}"
    )
    return train_df, val_df, test_df


def main():
    # 1. Load
    raw_df = load_raw_data()
    inspect_raw_data(raw_df)

    # 2. Clean
    clean_df = clean_pipeline(raw_df)

    # 3. EDA (on the full cleaned set, before splitting)
    run_eda(clean_df)

    # 4. Save the full cleaned dataset (useful for Phase 5's embedding step,
    #    which wants ALL historical tickets, not just the training split)
    PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    clean_df.to_csv(PROCESSED_DATA_PATH, index=False)
    logger.info(f"Saved full cleaned dataset to {PROCESSED_DATA_PATH}")

    # 5. Split and save train/val/test (used by Phases 8, 9, 10 for
    #    evaluating the Classification/Priority/Assignment agents)
    train_df, val_df, test_df = split_train_val_test(clean_df)
    train_df.to_csv(TRAIN_SPLIT_PATH, index=False)
    val_df.to_csv(VAL_SPLIT_PATH, index=False)
    test_df.to_csv(TEST_SPLIT_PATH, index=False)
    logger.info("Saved train/val/test splits")

    print("\n✅ Data pipeline complete. Files ready in data/processed/")


if __name__ == "__main__":
    main()
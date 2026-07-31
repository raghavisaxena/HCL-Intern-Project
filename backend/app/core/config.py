"""
Centralized application configuration.

This module reads values from the .env file (via pydantic-settings)
and exposes them as a single, typed `settings` object that the rest
of the application imports from.

Why this pattern?
- Type safety: if DEBUG is supposed to be a bool but someone puts "yes"
  in .env, Pydantic will raise a clear error at startup instead of a
  confusing bug later.
- Single source of truth: no more scattered os.getenv() calls.
- Easy testing: settings can be overridden in tests without touching .env.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- Application ---
    app_name: str = "IT Incident Ticket Assistant"
    app_env: str = "development"
    debug: bool = True

    # --- Database ---
    database_url: str = "postgresql://postgres:postgres@localhost:5432/incident_assistant_db"

    # --- Vector Store ---
    faiss_index_path: str = "../vectorstore/faiss_index"

    # --- Embedding Model ---
    embedding_model_name: str = "BAAI/bge-small-en-v1.5"

    # --- LLM ---
    llm_model_name: str = "microsoft/Phi-3-mini-4k-instruct"

    # --- Azure (placeholders, wired up in Phase 15) ---
    azure_ai_search_endpoint: str = ""
    azure_ai_search_key: str = ""
    azure_storage_connection_string: str = ""

    # Tells pydantic-settings where to find the .env file and how to
    # match .env keys (e.g. DATABASE_URL) to these lowercase fields.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# A single, shared instance every other module imports.
# Created once at import time — not re-read on every request.
settings = Settings()
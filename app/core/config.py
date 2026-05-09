from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]
PLACEHOLDER_API_KEYS = {"your_api_key_here", "your_real_key_here"}


class Settings(BaseSettings):
    app_name: str = "Enterprise IT Helpdesk Agent"
    upload_dir: str = str(BASE_DIR / "data" / "uploads")
    chroma_dir: str = str(BASE_DIR / "data" / "chroma")
    vector_store_dir: str = str(BASE_DIR / "data" / "chroma")
    chroma_collection: str = "it_helpdesk_knowledge"
    ticket_db_path: str = str(BASE_DIR / "data" / "tickets.db")
    log_file: str = str(BASE_DIR / "logs" / "app.log")
    log_level: str = "INFO"

    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    chat_model: str = "gpt-5.4"
    embeddings_model: str = "text-embedding-3-small"
    embedding_provider: str = "local"
    local_embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def has_openai_api_key(self) -> bool:
        return bool(self.openai_api_key and self.openai_api_key not in PLACEHOLDER_API_KEYS)

    def uses_openai_embeddings(self) -> bool:
        return self.embedding_provider.strip().lower() == "openai"


settings = Settings()

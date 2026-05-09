from app.core.config import Settings


def test_embedding_provider_defaults_to_local() -> None:
    settings = Settings(_env_file=None)

    assert settings.embedding_provider == "local"


def test_ticket_db_path_defaults_under_data_directory() -> None:
    settings = Settings(_env_file=None)

    assert settings.ticket_db_path.endswith("data\\tickets.db") or settings.ticket_db_path.endswith("data/tickets.db")


def test_has_openai_api_key_is_false_for_empty_value() -> None:
    settings = Settings(openai_api_key="", _env_file=None)

    assert settings.has_openai_api_key() is False


def test_has_openai_api_key_is_false_for_placeholder_value() -> None:
    settings = Settings(openai_api_key="your_api_key_here", _env_file=None)

    assert settings.has_openai_api_key() is False


def test_has_openai_api_key_is_true_for_real_value() -> None:
    settings = Settings(openai_api_key="sk-test-123", _env_file=None)

    assert settings.has_openai_api_key() is True


def test_uses_openai_embeddings_is_true_for_openai_provider() -> None:
    settings = Settings(embedding_provider="openai", _env_file=None)

    assert settings.uses_openai_embeddings() is True


def test_uses_openai_embeddings_is_false_for_local_provider() -> None:
    settings = Settings(embedding_provider="local", _env_file=None)

    assert settings.uses_openai_embeddings() is False

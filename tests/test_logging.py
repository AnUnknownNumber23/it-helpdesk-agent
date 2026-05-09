import logging
from pathlib import Path

from app.core import logging as app_logging


def test_configure_logging_writes_warning_to_file(tmp_path: Path, monkeypatch) -> None:
    log_file = tmp_path / "app.log"
    monkeypatch.setattr(app_logging.settings, "log_file", str(log_file))
    monkeypatch.setattr(app_logging.settings, "log_level", "INFO")

    app_logging.configure_logging()

    logger = logging.getLogger("app.services.query_service")
    logger.warning("test warning message")

    for handler in logging.getLogger().handlers:
        handler.flush()

    assert log_file.exists()
    assert "test warning message" in log_file.read_text(encoding="utf-8")

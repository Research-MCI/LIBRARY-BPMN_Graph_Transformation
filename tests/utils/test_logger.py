import logging
from app.utils.logger import LOG_FORMAT, get_logger


def test_logger_basic_log(tmp_path, caplog):
    # Custom log config
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    log_file = "test.log"
    config = {
        "LOG_LEVEL": "INFO",
        "LOG_DIR": str(log_dir),
        "LOG_FILE": log_file,
        "LOG_MAX_BYTES": 1024 * 10,
        "LOG_BACKUP_COUNT": 2,
    }

    logger = get_logger("test_logger_basic", config)
    msg = "Test log message"
    logger.info(msg)
    logger.error("Error message")

    log_path = log_dir / log_file
    assert log_path.exists(), "Log file must exist"

    with open(log_path, encoding="utf-8") as f:
        content = f.read()
        assert msg in content
        assert "Error message" in content
        # Check if format contains required fields
        assert "INFO in" in content or "ERROR in" in content


def test_logger_no_duplicate_handlers(tmp_path):
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    config = {
        "LOG_LEVEL": "DEBUG",
        "LOG_DIR": str(log_dir),
        "LOG_FILE": "dup.log",
        "LOG_MAX_BYTES": 1000,
        "LOG_BACKUP_COUNT": 1,
    }

    logger = get_logger("dup_logger", config)
    count1 = len(logger.handlers)
    # Call get_logger again, must not duplicate
    logger2 = get_logger("dup_logger", config)
    count2 = len(logger2.handlers)
    assert count1 == count2 == 2  # file + console


def test_logger_level_respected(tmp_path):
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    config = {
        "LOG_LEVEL": "WARNING",
        "LOG_DIR": str(log_dir),
        "LOG_FILE": "level.log",
        "LOG_MAX_BYTES": 1000,
        "LOG_BACKUP_COUNT": 1,
    }

    logger = get_logger("level_logger", config)
    logger.debug("Should not appear")
    logger.warning("Should appear")
    log_path = log_dir / "level.log"
    with open(log_path, encoding="utf-8") as f:
        content = f.read()
        assert "Should appear" in content
        assert "Should not appear" not in content


def test_logger_format_contains_fields(tmp_path):
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    config = {
        "LOG_LEVEL": "INFO",
        "LOG_DIR": str(log_dir),
        "LOG_FILE": "fmt.log",
        "LOG_MAX_BYTES": 1000,
        "LOG_BACKUP_COUNT": 1,
    }
    logger = get_logger("fmt_logger", config)
    logger.info("Hello formatting")
    log_path = log_dir / "fmt.log"
    with open(log_path, encoding="utf-8") as f:
        content = f.read()
        assert "Hello formatting" in content
        # Minimal field check (asctime, levelname, module, process)
        assert "INFO" in content
        assert "in" in content
        assert "process" in LOG_FORMAT


def test_logger_file_handler_error(monkeypatch):
    # Simulate permission error on file handler
    def fail_file_handler(*a, **kw):
        raise PermissionError("No permission for file handler")

    import app.utils.logger as logger_mod

    monkeypatch.setattr(logger_mod, "RotatingFileHandler", fail_file_handler)
    # Should fallback and not raise error
    logger = logger_mod.get_logger(
        "fail_logger",
        config={"LOG_LEVEL": "INFO", "LOG_DIR": "/invalid", "LOG_FILE": "fail.log"},
    )
    logger.info("Will only go to console (not file)")
    # If no exception, test passed


def test_logger_console_output(tmp_path):
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    log_file = "console.log"
    config = {
        "LOG_LEVEL": "INFO",
        "LOG_DIR": str(log_dir),
        "LOG_FILE": log_file,
        "LOG_MAX_BYTES": 1000,
        "LOG_BACKUP_COUNT": 1,
    }
    logger = get_logger(
        "console_logger",
        config=config,
    )
    logger.info("Console test message")
    log_path = log_dir / log_file
    with open(log_path, encoding="utf-8") as f:
        content = f.read()
        assert "Console test message" in content

"""Project-wide logger configuration."""

from __future__ import annotations

import logging
from logging import Logger


def get_logger(name: str = "nyayasetu", level: int = logging.INFO) -> Logger:
    """Return configured logger instance."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(level)
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False
    return logger

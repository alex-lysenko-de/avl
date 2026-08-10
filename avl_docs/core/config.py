"""Чтение config.ini приложения avl_docs."""

import configparser
from pathlib import Path

DEFAULT_DOCS_ROOT = r"C:\docs"

def _config_path() -> Path:
    return Path(__file__).resolve().parent.parent.parent / "config.ini"

def get_docs_root() -> Path:
    """Путь к файловому хранилищу приложения (см. wiki: Хранилище файлов приложения (C-docs))."""
    parser = configparser.ConfigParser()
    parser.read(_config_path(), encoding="utf-8")
    return Path(parser.get("storage", "docs_root", fallback=DEFAULT_DOCS_ROOT))

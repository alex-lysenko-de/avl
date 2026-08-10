"""Точка входа основного приложения avl_docs.

Заготовка: полноценный PySide6 GUI будет добавлен отдельными тикетами.
"""

from avl_docs.core.config import get_docs_root
from avl_docs.core.version import __version__


def main() -> int:
    print(f"avl_docs {__version__}")
    print(f"docs_root: {get_docs_root()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

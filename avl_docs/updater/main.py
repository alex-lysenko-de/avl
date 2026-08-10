"""Точка входа Updater avl_docs.

Заготовка: логика проверки и установки обновлений реализуется тикетом 109.
"""

from avl_docs.core.version import __version__


def main() -> int:
    print(f"avl_docs updater {__version__}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""demo — тестовая утилита для проверки механизма работы с тикетами.

v0.1: пустое окно. Требования к интерфейсу и поведению будут уточнены
следующими тикетами.
"""

import tkinter as tk

from avl_docs.core.version import __version__


def build_app() -> tk.Tk:
    root = tk.Tk()
    root.title(f"avl_docs demo {__version__}")
    return root


def main() -> int:
    app = build_app()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

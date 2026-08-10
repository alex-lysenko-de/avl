from avl_docs.demo.main import build_app


def test_demo_window_builds_and_closes():
    app = build_app()
    try:
        assert app.title().startswith("avl_docs demo")
    finally:
        app.destroy()

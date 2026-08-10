from avl_docs.core.version import __version__
from avl_docs.app.main import main as app_main
from avl_docs.updater.main import main as updater_main


def test_version_is_set():
    assert __version__


def test_app_entrypoint_runs():
    assert app_main() == 0


def test_updater_entrypoint_runs():
    assert updater_main() == 0

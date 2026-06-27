from __future__ import annotations

from triagecraft import __main__


def test_main_exists() -> None:
    assert callable(__main__.main)

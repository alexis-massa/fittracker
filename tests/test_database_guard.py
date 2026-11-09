import pytest

from src.db import db_manager


def test_tests_cannot_connect_to_the_real_database() -> None:
    with pytest.raises(RuntimeError, match="real database"):
        db_manager.connect()

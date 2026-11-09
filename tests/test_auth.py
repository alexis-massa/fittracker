import pytest

from src.auth import is_public_path
from src.auth import safe_redirect_target


@pytest.mark.parametrize(
    "path",
    ["/login", "/sw.js", "/static/manifest.webmanifest", "/static/icons/icon-192.png"]
    + ["/_nicegui/3.10.0/static/nicegui.js", "/_nicegui_ws/socket.io/"],
)
def test_assets_needed_before_login_are_public(path: str) -> None:
    assert is_public_path(path) is True


@pytest.mark.parametrize(
    "path",
    ["/", "/sessions/1", "/sessions/new", "/exercises", "/exercises/1/edit", "/login/extra"]
    + ["/static", "/sw.jsx", "/anything-else"],
)
def test_everything_else_requires_login(path: str) -> None:
    assert is_public_path(path) is False


@pytest.mark.parametrize("target", ["/", "/sessions/3", "/exercises?x=1"])
def test_local_paths_are_valid_redirect_targets(target: str) -> None:
    assert safe_redirect_target(target) == target


@pytest.mark.parametrize(
    "target",
    ["", "https://evil.example", "//evil.example", "/\\evil.example", "evil", "javascript:1"],
)
def test_anything_that_could_leave_the_site_redirects_home(target: str) -> None:
    assert safe_redirect_target(target) == "/"

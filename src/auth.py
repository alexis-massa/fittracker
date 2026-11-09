# src/auth.py
from urllib.parse import quote

from nicegui import app
from nicegui import context
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.responses import Response

from src.models import user as user_model
from src.models.user import User
from src.utils.throttle import LoginThrottle

SESSION_KEY = "user_id"
login_throttle = LoginThrottle()

# Reachable without logging in. Everything else - every page, including any
# added later - requires a session. These serve no user data.
_PUBLIC_PREFIXES = ("/_nicegui", "/static/")
_PUBLIC_PATHS = ("/login", "/sw.js")


def is_public_path(path: str) -> bool:
    return path in _PUBLIC_PATHS or path.startswith(_PUBLIC_PREFIXES)


def safe_redirect_target(target: str) -> str:
    """Only allow local paths, so a login link can't bounce users to another site."""
    if target.startswith("/") and not target.startswith("//") and "\\" not in target:
        return target
    return "/"


def login(user: User) -> None:
    app.storage.user[SESSION_KEY] = user.id


def logout() -> None:
    app.storage.user.pop(SESSION_KEY, None)


def session_user() -> User | None:
    """The user the current browser session is logged in as, if they still exist."""
    user_id = app.storage.user.get(SESSION_KEY)
    if user_id is None:
        return None
    user = user_model.get_by_id(user_id)
    if user is None:
        logout()
    return user


def current_user() -> User:
    """The logged-in user, from inside a page or one of its event handlers."""
    user: User | None = getattr(context.client.request.state, "user", None)
    if user is None:
        raise RuntimeError("No logged-in user: this page was reached without authentication.")
    return user


def current_user_id() -> int:
    return current_user().id


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if is_public_path(request.url.path):
            return await call_next(request)
        user = session_user()
        if user is None:
            destination = request.url.path + (f"?{request.url.query}" if request.url.query else "")
            return RedirectResponse(f"/login?redirect_to={quote(destination)}")
        request.state.user = user
        return await call_next(request)

FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:0.6.14 /uv /uvx /usr/local/bin/

# Match the host dev user's UID/GID so files created in the bind-mounted
# project dir (.venv, etc.) aren't root-owned on the host.
ARG UID=1000
ARG GID=1000
RUN groupadd -g ${GID} app && useradd -m -u ${UID} -g ${GID} app

WORKDIR /app
RUN chown app:app /app
USER app

COPY --chown=app:app pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

COPY --chown=app:app . .
RUN uv sync --frozen --no-dev

EXPOSE 8080

# Run the venv's own interpreter directly rather than "uv run" - uv run
# re-syncs against the default dependency groups (dev included) on every
# invocation, undoing the --no-dev image above and adding a network call
# on every container start.
CMD [".venv/bin/python", "main.py"]

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
RUN uv sync --frozen --no-install-project

COPY --chown=app:app . .
RUN uv sync --frozen

EXPOSE 8080

CMD ["uv", "run", "python", "main.py"]

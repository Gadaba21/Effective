FROM python:3.11-slim AS base
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_VERSION=0.6.14 \
    PIP_UVICORN_VERSION=0.34.0
WORKDIR /app_dir

FROM base AS builder

RUN pip install --upgrade "uv~=$UV_VERSION"
ADD pyproject.toml ./
RUN uv sync

FROM base AS final

RUN pip install --upgrade "uvicorn~=$PIP_UVICORN_VERSION"
COPY --from=builder /app_dir/.venv ./.venv
ADD app ./app/
CMD ["/app_dir/.venv/bin/python3", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
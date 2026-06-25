ARG PYTHON_VERSION=3.13
ARG UV_IMAGE=ghcr.io/astral-sh/uv
ARG UV_TAG=python${PYTHON_VERSION}-trixie-slim
ARG NONROOT_UID=999
ARG NONROOT_GID=999
ARG NONROOT_USER=appuser

FROM ${UV_IMAGE}:${UV_TAG} AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_DEV=1 \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# This only installs the dependencies of the project and caches them for later builds
# as this is a demo project, all Dockerimages shall source from the same pyproject.toml
# this might increase the layer-size a bit, given unneeded resources, but again, this is a demo
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock,readonly \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml,readonly \
    uv sync --locked --no-install-project --group api

FROM runtime-base:latest

COPY --from=builder --chown=${NONROOT_UID}:${NONROOT_GID} /app /app

COPY src/serve/ .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

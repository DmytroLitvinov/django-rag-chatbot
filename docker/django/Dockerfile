# syntax = docker/dockerfile:1
# This Dockerfile uses multi-stage build to customize DEV and PROD images:
# https://docs.docker.com/develop/develop-images/multistage-build/

FROM docker.io/python:3.13.7-slim-bookworm as development_build
COPY --from=ghcr.io/astral-sh/uv:0.8.17 /uv /uvx /bin/

LABEL maintainer="myapp.com"
LABEL vendor="myapp.com"

# `DJANGO_ENV` arg is used to make prod / dev builds:
ARG DJANGO_ENV \
  # Needed for fixing permissions of files created by Docker:
  UID=1000 \
  GID=1000

ENV DJANGO_ENV=${DJANGO_ENV} \
  # python:
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PYTHONDONTWRITEBYTECODE=1 \
  # pip:
  PIP_NO_CACHE_DIR=1 \
  PIP_DISABLE_PIP_VERSION_CHECK=1 \
  PIP_DEFAULT_TIMEOUT=100 \
  PIP_ROOT_USER_ACTION=ignore \
  # uv:
  # https://rob.cogit8.org/posts/optimizing-django-docker-builds-with-astrals-uv/
  # Enable bytecode compilation
  UV_COMPILE_BYTECODE=1 \
  # Copy from the cache instead of linking since it's a mounted volume
  UV_LINK_MODE=copy \
  UV_CACHE_DIR=/app/.cache/uv \
  # Prevents uv from trying to manage Python installations. In Docker container, we already have Python installed
  # and don’t want uv attempting to download or manage different Python versions.
  UV_NO_MANAGED_PYTHON=1 \
  # https://github.com/astral-sh/uv/pull/6834#issuecomment-2319253359
  # # Use the system Python environment
  UV_PROJECT_ENVIRONMENT="/usr/local/" \
  # Whether uv should allow Python downloads
  UV_PYTHON_DOWNLOADS=never \
  # tini:
  TINI_VERSION=v0.19.0

SHELL ["/bin/bash", "-eo", "pipefail", "-c"]

# System deps (we don't use exact versions because it is hard to update them,
# pin when needed):
# hadolint ignore=DL3008
RUN apt-get update && apt-get upgrade -y \
  && apt-get install --no-install-recommends -y \
    bash \
    brotli \
    build-essential \
    curl \
    gettext \
    git \
    # For pycairo:
    libpq-dev \
    xorg-dev \
    libxcursor-dev \
    libxrandr-dev \
    libxinerama-dev \
    mesa-common-dev  \
    libgl1-mesa-dev  \
    libglu1-mesa-dev \
  # Installing `tini` utility:
  # https://github.com/krallin/tini
  # Get architecture to download appropriate tini release:
  # See https://github.com/wemake-services/wemake-django-template/issues/1725
  && dpkgArch="$(dpkg --print-architecture | awk -F- '{ print $NF }')" \
  && curl -o /usr/local/bin/tini -sSLO "https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini-${dpkgArch}" \
  && chmod +x /usr/local/bin/tini && tini --version \
  # Cleaning cache:
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && apt-get clean -y && rm -rf /var/lib/apt/lists/*

WORKDIR /code

RUN groupadd -g "${GID}" -r web \
  && useradd -d '/code' -g web -l -r -u "${UID}" web \
  && chown web:web -R '/code' \
  # Static and media files:
  && mkdir -p '/var/www/django/static' '/var/www/django/media' \
  && chown web:web '/var/www/django/static' '/var/www/django/media'

# Copy only requirements, to cache them in docker layer:
COPY --chown=web:web ./uv.lock ./pyproject.toml /code/

# Project initialization:
# hadolint ignore=SC2046
RUN --mount=type=cache,target=/app/.cache/uv \
  echo "$DJANGO_ENV" \
  && uv --version \
  && uv sync --locked

# This is a special case. We need to run this script as an entry point:
COPY ./docker/django/entrypoint.sh /docker-entrypoint.sh

# Setting up proper permissions:
RUN chmod +x '/docker-entrypoint.sh' \
  # Replacing line separator CRLF with LF for Windows users:
  && sed -i 's/\r$//g' '/docker-entrypoint.sh'

# Running as non-root user:
USER web

# We customize how our app is loaded with the custom entrypoint:
ENTRYPOINT ["tini", "--", "/docker-entrypoint.sh"]


# The following stage is only for production:
# https://wemake-services.github.io/wemake-django-template/pages/template/production.html
FROM development_build AS production_build
COPY --chown=web:web . /code

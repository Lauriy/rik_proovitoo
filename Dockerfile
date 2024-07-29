FROM python:3.12-slim AS base

LABEL maintainer="Lauri Elias <laurileet@gmail.com>"

# So we'd never have a stuck build waiting for input
ARG DEBIAN_FRONTEND=noninteractive

# Waste of microseconds, I trust the base image to be up to date
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
# So the very last log entry before a crash would be recorded
ENV PYTHONUNBUFFERED=1
# To avoid writing .pyc files which may interfere during development
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /home/docker/rik_proovitöö

COPY manage.py requirements.txt ./

# Buildkit style cache mount to speed up repeated builds
RUN --mount=type=cache,target=/root/.cache/pip pip install --no-cache-dir -r requirements.txt && rm -rf requirements.txt

COPY docker-entrypoint.sh /usr/bin/

RUN chmod +x /usr/bin/docker-entrypoint.sh

# We put defaults we don't want to repeat and rarely changed files into this stage
ENTRYPOINT ["docker-entrypoint.sh"]

FROM base AS development

# Django's built-in development server
EXPOSE 8000

COPY requirements.test.txt pytest.ini ./

RUN --mount=type=cache,target=/root/.cache/pip pip install --no-cache-dir -r requirements.test.txt  \
    && rm -rf requirements.test.txt

# We need the main source code to do anything useful
COPY rik_proovitöö ./rik_proovitöö

# TDD is a thing these days I hear, also allows us to reuse this stage for both 'dev' and 'test' profiles
COPY rik_proovitöö_tests ./rik_proovitöö_tests

FROM base AS production

# Let's allow .pycs again
ENV PYTHONDONTWRITEBYTECODE=0

# Needed to compile uwsgi, clean up after
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libpcre3-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN --mount=type=cache,target=/root/.cache/pip pip --no-cache-dir install uwsgi

COPY uwsgi.ini ./

# Best practice not to give pwners free root
RUN useradd -m docker
RUN mkdir -p /home/docker/rik_proovitöö/run /home/docker/rik_proovitöö/static_collected
RUN chown -R docker:docker /home/docker/rik_proovitöö
RUN chmod 755 /home/docker/rik_proovitöö/run
USER docker

COPY rik_proovitöö ./rik_proovitöö

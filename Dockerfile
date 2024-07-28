FROM python:3.12-slim AS base

LABEL maintainer='Lauri Elias <laurileet@gmail.com>'

WORKDIR /home/docker/rik_proovitöö

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY manage.py ./

COPY rik_proovitöö ./rik_proovitöö

COPY docker-entrypoint.sh /usr/bin/

RUN chmod +x /usr/bin/docker-entrypoint.sh

ENTRYPOINT ["docker-entrypoint.sh"]

FROM base AS development

COPY requirements.test.txt pytest.ini ./

COPY rik_proovitöö_tests ./rik_proovitöö_tests

RUN pip install -r requirements.test.txt

FROM base AS production

RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libpcre3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uwsgi

COPY uwsgi.ini ./

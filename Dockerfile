FROM python:3.12

LABEL maintainer='Lauri Elias <laurileet@gmail.com>'

RUN apt-get update && apt-get install uwsgi -y

WORKDIR /home/docker/rik_proovitöö

RUN mkdir -p /home/docker/rik_proovitöö/run && chmod -R 755 /home/docker/rik_proovitöö/run

COPY requirements.txt ./

RUN pip install -r requirements.txt && pip install uwsgi

COPY manage.py uwsgi.ini ./

COPY docker-entrypoint.sh /usr/bin/

COPY rik_proovitöö ./rik_proovitöö

RUN chmod +x /usr/bin/docker-entrypoint.sh

# EXPOSE 8000

# No single quotes!
ENTRYPOINT ["docker-entrypoint.sh"]

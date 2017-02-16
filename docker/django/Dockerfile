FROM python:3.6.0

ENV PYTHONUNBUFFERED 1

COPY ./docker/django/django-entrypoint.sh /
COPY ./docker/django/worker-entrypoint.sh /
COPY ./docker/django/scheduler-entrypoint.sh /
COPY ./py-requirements /django/py-requirements

WORKDIR /django

RUN pip install pip==9.0.1
RUN pip install -r py-requirements/dev.txt

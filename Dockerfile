FROM python:3.11-slim-bullseye AS build

RUN apt-get -y update && \
    apt-get -y upgrade && \
    apt-get -y clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /usr/application

RUN python -m venv /usr/application/venv
ENV PATH="/usr/application/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir uv && \
    uv pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim-bullseye

RUN apt-get -y update && \
    apt-get -y upgrade && \
    rm -rf /var/lib/apt/lists/* && \
    groupadd -g 999 python && \
    useradd -r -u 999 -g python python && \
    mkdir /usr/application && \
    mkdir /temp && \
    chown python:python /usr/application && \
    chown python:python /temp && \
    chmod 777 /temp

WORKDIR /usr/application

COPY --chown=python:python --from=build /usr/application/venv ./venv
COPY --chown=python:python . .

USER 999
ENV PATH="/usr/application/venv/bin:$PATH"

EXPOSE 8000
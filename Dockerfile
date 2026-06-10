FROM python:3.12.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


WORKDIR /usr/src/app


COPY req.txt req.txt

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r req.txt

COPY . .


FROM python:alpine

WORKDIR /usr/src/app
ENV S3A_THREADS 4
ENV S3A_LiSTENER_IP 0.0.0.0
ENV S3A_LiSTENER_PORT 8080


RUN apk --no-cache add build-base

COPY setup.cfg ./
COPY pyproject.toml ./
RUN pip install -e .

RUN mkdir -p s3app
COPY s3app/ ./s3app/

ENTRYPOINT ["/bin/sh", "-c", "s3app --threads=$S3A_THREADS --host=$S3A_LiSTENER_IP --port=$S3A_LiSTENER_PORT"]
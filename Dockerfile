FROM python:alpine

WORKDIR /usr/src/app

RUN apk --no-cache add build-base openldap-dev

COPY setup.cfg ./
COPY pyproject.toml ./
RUN pip install .

RUN mkdir -p /usr/local/bin/s3app
COPY s3app/ /usr/local/bin/s3app/

ENV S3APP_THREADS 4
ENV S3APP_LISTENER_IP 0.0.0.0
ENV S3APP_LISTENER_PORT 8080

ENTRYPOINT ["/bin/sh", "-c", "s3app-run --threads=$S3APP_THREADS --host=$S3APP_LISTENER_IP --port=$S3APP_LISTENER_PORT"]
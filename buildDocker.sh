#!/bin/sh
VERSION=1.2.1
docker rmi python:alpine
docker build . -t yotronpublic/s3app:$VERSION
docker push yotronpublic/s3app:$VERSION
docker tag yotronpublic/s3app:$VERSION yotronpublic/s3app:latest
docker push yotronpublic/s3app:latest
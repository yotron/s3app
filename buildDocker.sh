#!/bin/sh
VERSION=1.0.0
docker build . -t yotronpublic/s3app:$VERSION
docker push yotronpublic/s3app:$VERSION
docker tag yotronpublic/s3app:$VERSION yotronpublic/s3app:latest
docker push yotronpublic/s3app:latest
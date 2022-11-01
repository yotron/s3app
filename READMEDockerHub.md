[![yotron](https://www.yotron.de/img/logo-yotron.png)](https://www.yotron.de)

[YOTRON](https://www.yotron.de) is a consultancy company which is focused on DevOps, Cloudmanagement and
Data Management with NOSQL and SQL-Databases. Visit us on [ www.yotron.de ](https://www.yotron.de).

# S3App
S3 (Simple Storage Solution) is a file storage services which is part of Cloud solutions. It is known for its
scalability, data availability, security, performance and the ease to connect storage clients to it. Introduced by Amazon in AWS, other
provider of managed S3 are available just like software solutions to set up an private S3-solution like ([Ceph](https://ceph.io/) or [Cloudian](https://cloudian.com/)).

**S3App simplifies** the access to a S3Buckets with a provider independent web based frontend which allows
the visualizing and the management of the content of S3 buckets.

For further information and the manual, please see [YOTRON/s3app](https://www.yotron.de/s3app/)

# URLs
The project contains code, build packages, container ... . Below an overview:

| Type                  | Provider                        | URL                                                           |
|-----------------------|---------------------------------|---------------------------------------------------------------|
| S3App Manual          | yotron.de                       | https://www.yotron.de/s3app/                                  |
| Container             | hub.docker.com                  | https://hub.docker.com/r/yotronpublic/s3app                   | 
| Python Package (PyPi) | pypi.org                        | https://pypi.org/project/s3app/                               |  
| HELM package          | artifacthub.io / helm.yotron.de | https://artifacthub.io/packages/helm/yotron-helm-charts/s3app |
| Code/Contribution     | github.com                      | https://github.com/yotron/s3app/                              |
| Problems/Feedback     | github.com                      | https://github.com/yotron/s3app/issues                        |

# Configurations
The following Env Variables are needed to run this container:

| Name                | Default | Description                                                                                                               | 
|---------------------|---------|---------------------------------------------------------------------------------------------------------------------------|
| S3APP_LISTENER_IP   | 0.0.0.0 | Listener Host IP. 0.0.0.0 for all IPs.                                                                                    |
| S3APP_LISTENER_PORT | 8080    | Listener Host Port                                                                                                        |
| S3APP_THREADS       | 4       | Threads for parallelization                                                                                               |
| S3APP_CONF_FILE     | ""      | Local Path to the .env file with the S3App configuration. Please see README in [Github](https://github.com/yotron/s3app/) |

[![yotron](https://www.yotron.de/img/logo-yotron.png)](http://www.yotron.de)

[YOTRON](http://www.yotron.de) is a consultancy company which is focused on DevOps, Cloudmanagement and
Data Management with NOSQL and SQL-Databases. Visit us on [www.yotron.de](http://www.yotron.de)
ement with NOSQL and SQL-Databases.

# S3App
## Description
S3 (Simple Storage Solution) is a file storage services which is part of Cloud solutions. It is known for its
scalability, data availability, security, performance and the ease to connect storage clients to it. Introduced by Amazon in AWS, other
provider of managed S3 are available just like software solutions to set up an private S3-solution like ([Ceph](https://ceph.io/) or [Cloudian](https://cloudian.com/)).

**S3App simplifies** the access to a S3Buckets with a provider independent web based frontend which allows
the visualizing and the management of the content of S3 buckets.

For further information and the manual, please see [s3app/manual](http://192.168.56.105:1313/s3app/manual/)

## Content
This HELM package contains th following applications:

| name       | description                                                                                                      |
|------------|------------------------------------------------------------------------------------------------------------------|
| S3App      | A web application to visualize and to manage the content of S3Bucket independently from Acceess- or Secret-Keys. |
| NGINX      | An optional Reverse Proxy as a Kubernetes sidecar to S3App for security and TLS termination (https)              | 
| PostgreSQL | An optional mwtadata database. Not needed for testing and can be provided externally.                            |

## URLs

The project contains code, build packages, container ... . Below an overview:

| Type                  | Provider                        | URL                                                           |
|-----------------------|---------------------------------|---------------------------------------------------------------|
| S3App Manual          | yotron.de                       | http://www.yotron.de/s3app/                                   |
| Container             | hub.docker.com                  | https://hub.docker.com/repository/docker/yotronpublic/s3app   | 
| Python Package (PyPi) | pypi.org                        | https://pypi.org/project/s3app/                               |  
| HELM package          | artifacthub.io / helm.yotron.de | https://artifacthub.io/packages/helm/yotron-helm-charts/s3app |
| Code/Contribution     | github.com                      | https://github.com/yotron/s3app/                              |
| Problems/Feedback     | github.com                      | https://github.com/yotron/s3app/issues                        |

## Prerequisites

- HELM 3

## Dependencies
The following dependencies are included in that package.

| name                                                                               | description                                                                       |
|------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| [k8s-secrets](https://artifacthub.io/packages/helm/yotron-helm-charts/k8s-secrets) | An application free package to simplify the deployment of secrets to Kubernetes.  |
| [PostgreSQL by Bitnami](https://bitnami.com/stack/postgresql/helm)                 | A optional package if you want to deploy a PostgreSQL additionally.               |  
 

## Installation
### Fast installation
You can install a fully functional S3App for testing and demonstration without the need of a configuration.  

```
helm repo add yotron-apps http://helm.yotron.de/
helm install s3app yotron-apps/s3app
```

S3App is now reachable with a NodePort service under http://<Kubernetes Node IP>:31005

### Integration as a Chart dependency
To integrate S3App into you project Chart, please add the HELM package to your own HELM project:
```
dependencies:
  - name: s3app
    version: <the version you want>
    repository: http://helm.yotron.de/
```

# HELM Configuration

### S3App Customization Parameter
| Name            | Default                                   | Example | Description                                                         |
|-----------------|-------------------------------------------|---------|---------------------------------------------------------------------|
| customize.title | S3App by YOTRON                           |         | Title of your project.                                              |
| customize.icon  | https://www.yotron.de/img/yotron_logo.svg |         | Icon to be used in the Header. Can be any URL to an png, svg, ... . |

### Log and Server Parameter
| Name         | Default | Example                 | Description                                                                                   |
|--------------|---------|-------------------------|-----------------------------------------------------------------------------------------------|
| logLevel     | info    |                         | LogLevel for the Logging. Can be: fatal, error, warning, info, debug                          | 
| hostnames    | []      | ["s3app.k8s.yotron.de"] | Mandatory for Ingress and Reverse Proxy: List of hosts the S3App Web server is listening on.  |
| listenerPort | 80      |                         | The port of S3App Web Server is listening on, like https://s3app.k8s.yotron.de:443            |
| listenerIPs  |         | ["192.168.56.249"]      | IPs S3App shall listen on. Must be set to allow external Access to the app directly.          |

### General K8S Parameter
| Name                    | Default  | Example                                             | Description                                                                     |
|-------------------------|----------|-----------------------------------------------------|---------------------------------------------------------------------------------|
| k8s.identifier          | s3app    |                                                     | Identifier for the Kubernetes Resources                                         |
| k8s.annotations         | {}       | yotron.de/created_by: s3app                         | Dictionary of annotations added too all Kuberentes resources in the deployment. |
| k8s.service.annotations | {}       | metallb.universe.tf/loadBalancerIPs: 192.168.56.249 | Dictionary of annotations added to the Kubernetes service of S3App.             |
| k8s.service.type        | NodePort |                                                     | Type of the Kubernetes Service. Could be ClusterIP, NodePort, LoadBalancer, ... |
| k8s.service.nodePort    |          | 31005                                               | NodePort the S3App Service is reachable as a Kubernetes NodePort service.       |

### S3App Image, database and Performance Parameter
| Name                         | Default            | Example           | Description                                                                                                                 |
|------------------------------|--------------------|-------------------|-----------------------------------------------------------------------------------------------------------------------------|
| secretKey                    | changeMySecret     |                   | A key which used to sign session cookies for protection against cookie data tampering. In production please change it.      |
| server.replicas              | 1                  |                   | Parallelization of S3App-Pods. Increase the to allow High Availability or a higher performance if needed-                   |
| server.threadsPerReplica     | 4                  |                   | Thread per S3App Pod allowed to run.                                                                                        |
| server.image                 | yotronpublic/s3app |                   | Docker Image URl of S3App.                                                                                                  |
| server.imagePullPolicy       | IfNotPresent       |                   | Is set to IfNotPresent to pull the Docker image only if needed.                                                             |
| server.tag                   | latest             |                   | Set the tag of the Docker Image you want to deploy.                                                                         |
| server.database.type         | sqlite             |                   | Set the type of databse to store the S3App metadata. Must be `sqlite` or `postgres`.                                        |
| server.database.pgInternal   | true               |                   | Set to `false` if you want to use a external PostgreSQL. Set to `true` to use the PostgreSQL deployed by this HELM package. |
| server.database.pgDbHost     |                    | postgres.mydb.net | Only when `pgInternal`: `false`: The host of the external PostgreSQL                                                        |
| server.database.pgDbPort     | 5432               |                   | Only when `pgInternal`: `false`: The listener port of the external PostgreSQL                                               |
| server.database.pdDbName     |                    | s3app             | Only when `pgInternal`: `false`: The database name of the external PostgreSQL                                               |
| server.database.pgDbUserName |                    | s3app             | Only when `pgInternal`: `false`: The user name to authenticate against the external PostgreSQL                              |
| server.database.pgDbUserPw   |                    | s3app             | Only when `pgInternal`: `false`: The password to authenticate against the external PostgreSQL                               |
|
For performance tuning please read our remarks in [Github](https://github.com/yotron/s3app/)

### TLS Parameter
| Name           | Default | Example              | Description                                                                                                                                                                                     |
|----------------|---------|----------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| tls.enabled    | false   |                      | Set to `true` to activate TLS termination (https) for the communication with S3App. Teh TLS setting is used for the Reverse Proxy and the Ingress Resource when active.                         |
| tls.secretName |         | defaultSelfSigned    | The secret name with the cert and key to use for TLS-termination.  You can define the secret externally (secret type `kubernetes.io/tls`or use the parameter `certs.tls` to create the secret.) |
| certs.tls      |         | see values.yaml file | Create a separated TLS cert and key pair with a name to allow TLS-termination with the Reverse Proxy or the Ingress Resources. Teh name is used in `tls.secretName`                             |

### Reverse Proxy Parameter
| Name                            | Default       | Example | Description                                                  |
|---------------------------------|---------------|---------|--------------------------------------------------------------|
| nginxproxy.enabled              | true          |         | Set to true to add a NGINX Reverse Proxy as a sidecar.       |
| nginxproxy.image                | nginx         |         | Name of the Docker image of the NGINX application.           |
| nginxproxy.tag                  | 1.23.1-alpine |         | Tag of the Docker image of the NGINX application to use      |
| nginxproxy.clientMaxBodySize    | 10m           |         | Set the max. size of the file to be uploaded.                |
| nginxproxy.clientConnectTimeout | 90            |         | Set the time out for idled connections in seconds.           |
| nginxproxy.proxySendTimeout     | 90            |         | Set the request time out during idling during send requests. |
| nginxproxy.proxyReadTimeout     | 90            |         | Set the request time out during idling of read requests.     |

### Kubernetes Ingress Parameter
| Name                     | Default | Example | Description                                                              |
|--------------------------|---------|---------|--------------------------------------------------------------------------|
| ingress.enabled          | false   |         | Set to `true` to add S3App to the ingress controlling of Kubernetes.     |
| ingress.annotations      | {}      |         | Dictionary with annotations added to the Ingress resource in Kubernetes. |
| ingress.ingressClassName | nginx   |         | Dictionary with annotations added to the Ingress resource in Kubernetes. |
| ingress.path             | "/"     |         | Path of the Ingress route.                                               |
| ingress.pathType         | Prefix  |         | PathType of the Ingress route.                                           |



### PostgreSQL
For are providing a base setuo for the internal PostgreSQL by Bitnami, which is automatically connected to S3App. The complete configuration of the Bitnami PostgreSQL database
you find in [artifacthub.io](https://artifacthub.io/packages/helm/bitnami/postgresql)

| Name                                            | Default    | Example | Description                                                                                                   |
|-------------------------------------------------|------------|---------|---------------------------------------------------------------------------------------------------------------|
| postgresql.fullnameOverride                     | postgresql |         | String to fully override common.names.fullname template                                                       |
| postgresql.architecture                         | standalone |         | PostgreSQL architecture (standalone or replication)                                                           |
| postgresql.auth.postgresPassword                | postgres   |         | Password for the "postgres" admin user. Ignored if auth.existingSecret with key postgres-password is provided |
| postgresql.auth.username                        | s3app      |         | Name for a custom user to create                                                                              |
| postgresql.auth.password                        | s3app      |         | Password for the custom user to create. Ignored if auth.existingSecret with key password is provided          |
| postgresql.auth.database                        | s3app      |         | Name for a custom database to create                                                                          |
| postgresql.primary.service.type                 | ClusterIP  |         | Kubernetes Service type                                                                                       |
| postgresql.primary.service.nodePorts.postgresql | 31000      |         | Node port for PostgreSQL                                                                                      |
| postgresql.primary.persistence.enabled          | true       |         | Enable PostgreSQL Primary data persistence using PVC                                                          |
| postgresql.primary.persistence.size             | 1Gi        |         | PVC Storage Request for PostgreSQL volume                                                                     |

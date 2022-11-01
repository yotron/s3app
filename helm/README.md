[![yotron](https://www.yotron.de/img/logo-yotron.png)](https://www.yotron.de)

[YOTRON](https://www.yotron.de) is a consultancy company which is focused on DevOps, Cloudmanagement and
Data Management with NOSQL and SQL-Databases. Visit us on [www.yotron.de](https://www.yotron.de).

# S3App
## Description
S3 (Simple Storage Solution) is a file storage services which is part of Cloud solutions. It is known for its
scalability, data availability, security, performance and the ease to connect storage clients to it. Introduced by Amazon in AWS, other
provider of managed S3 are available just like software solutions to set up an private S3-solution like ([Ceph](https://ceph.io/) or [Cloudian](https://cloudian.com/)).

**S3App simplifies** the access to a S3Buckets with a provider independent web based frontend which allows
the visualizing and the management of the content of S3 buckets.

For further information and the manual, please see [YOTRON/s3app](https://www.yotron.de/s3app/)

## Content
This HELM package contains th following applications:

| name       | description                                                                                                      |
|------------|------------------------------------------------------------------------------------------------------------------|
| S3App      | A web application to visualize and to manage the content of S3Bucket independently from Acceess- or Secret-Keys. |
| NGINX      | An optional Reverse Proxy as a Kubernetes sidecar to S3App for security and TLS termination (https)              | 
| PostgreSQL | An optional metadata database. Not needed for testing and can be provided externally.                            |

## URLs

The project contains code, build packages, container ... . Below an overview:

| Type                  | Provider                        | URL                                                           |
|-----------------------|---------------------------------|---------------------------------------------------------------|
| S3App Manual          | yotron.de                       | https://www.yotron.de/s3app/                                  |
| Container             | hub.docker.com                  | https://hub.docker.com/r/yotronpublic/s3app                   | 
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
| Name            | Default                                   | Example | Description                                                         | Config Parameter [(docu)](https://github.com/yotron/s3app/) |
|-----------------|-------------------------------------------|---------|---------------------------------------------------------------------|-------------------------------------------------------------|
| customize.title | S3App by YOTRON                           |         | Title of your project.                                              | S3APP_APP_NAME                                              |
| customize.icon  | https://www.yotron.de/img/yotron_logo.svg |         | Icon to be used in the Header. Can be any URL to an png, svg, ... . | S3APP_APP_ICON                                              |

### Log and Server Parameter
| Name         | Default | Example                 | Description                                                                                   | Config Parameter [(docu)](https://github.com/yotron/s3app/) |
|--------------|---------|-------------------------|-----------------------------------------------------------------------------------------------|-------------------------------------------------------------|
| logLevel     | info    |                         | LogLevel for the Logging. Can be: fatal, error, warning, info, debug                          | S3APP_LOG_LEVEL                                             |
| hostnames    | []      | ["s3app.k8s.yotron.de"] | Mandatory for Ingress and Reverse Proxy: List of hosts the S3App Web server is listening on.  |                                                             |
| listenerPort | 80      |                         | The port of S3App Web Server is listening on, like https://s3app.k8s.yotron.de:443            |                                                             |
| listenerIPs  |         | ["192.168.56.249"]      | IPs S3App shall listen on. Must be set to allow external Access to the app directly.          |                                                             |

### General K8S Parameter
| Name                    | Default  | Example                                             | Description                                                                     |
|-------------------------|----------|-----------------------------------------------------|---------------------------------------------------------------------------------|
| k8s.identifier          | s3app    |                                                     | Identifier for the Kubernetes Resources                                         |
| k8s.annotations         | {}       | yotron.de/created_by: s3app                         | Dictionary of annotations added too all Kuberentes resources in the deployment. |
| k8s.service.annotations | {}       | metallb.universe.tf/loadBalancerIPs: 192.168.56.249 | Dictionary of annotations added to the Kubernetes service of S3App.             |
| k8s.service.type        | NodePort |                                                     | Type of the Kubernetes Service. Could be ClusterIP, NodePort, LoadBalancer, ... |
| k8s.service.nodePort    |          | 31005                                               | NodePort the S3App Service is reachable as a Kubernetes NodePort service.       |

### S3App Image, database and Performance Parameter
| Name                             | Default            | Example           | Description                                                                                                                 | Config Parameter [(docu)](https://github.com/yotron/s3app/) |
|----------------------------------|--------------------|-------------------|-----------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------|
| app.secretKey                    | changeMySecret     |                   | A key which used to sign session cookies for protection against cookie data tampering. In production please change it.      | S3APP_SECRET_KEY                                            |
| app.server.replicas              | 1                  |                   | Parallelization of S3App-Pods. Increase the to allow High Availability or a higher performance if needed-                   |                                                             |
| app.server.threadsPerReplica     | 4                  |                   | Thread per S3App Pod allowed to run.                                                                                        |                                                             |
| app.server.image                 | yotronpublic/s3app |                   | Docker Image URl of S3App.                                                                                                  |                                                             |
| app.server.imagePullPolicy       | IfNotPresent       |                   | Is set to IfNotPresent to pull the Docker image only if needed.                                                             |                                                             |
| app.server.tag                   | latest             |                   | Set the tag of the Docker Image you want to deploy.                                                                         |                                                             |
| app.server.database.type         | sqlite             |                   | Set the type of databse to store the S3App metadata. Must be `sqlite` or `postgres`.                                        | S3APP_DB_TYPE                                               |
| app.server.database.pgInternal   | true               |                   | Set to `false` if you want to use a external PostgreSQL. Set to `true` to use the PostgreSQL deployed by this HELM package. |                                                             |
| app.server.database.pgDbHost     |                    | postgres.mydb.net | Only when `pgInternal`: `false`: The host of the external PostgreSQL                                                        | S3APP_PG_DB_HOST                                            |
| app.server.database.pgDbPort     | 5432               |                   | Only when `pgInternal`: `false`: The listener port of the external PostgreSQL                                               | S3APP_PG_DB_PORT                                            |
| app.server.database.pdDbName     |                    | s3app             | Only when `pgInternal`: `false`: The database name of the external PostgreSQL                                               | S3APP_PG_DB_NAME                                            |
| app.server.database.pgDbUserName |                    | s3app             | Only when `pgInternal`: `false`: The user name to authenticate against the external PostgreSQL                              | S3APP_PG_DB_USER_NAME                                       |
| app.server.database.pgDbUserPw   |                    | s3app             | Only when `pgInternal`: `false`: The password to authenticate against the external PostgreSQL                               | S3APP_PG_DB_USER_PW                                         |
| app.configs                      |                    |                   | Map with additional configurations for Flask Appbuilder.                                                                    |                                                             |
|
For performance tuning please read our remarks in [Github](https://github.com/yotron/s3app/)

### Authentication general
| name                      | Default  | Example | Description                                                                                                                             | Config Parameter [(docu)](https://github.com/yotron/s3app/) | 
|---------------------------|----------|---------|-----------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------|
| auth.type                 | database | ldap    | Parameter to define the authentication method. It can be an authentication via LDAP or via the default database with name and password. | S3APP_AUTH_TYPE                                             |
| auth.userRegistration     | false    |         | Parameter to define if a user can self registrate to S3App. With LDAP it must be set to True.                                           | AUTH_USER_REGISTRATION                                      |
| auth.userRegistrationRole | S3User   |         | Default role a user, when registered or authenticated via LDAP firstly.                                                                 | AUTH_USER_REGISTRATION_ROLE                                 |
| auth.rolesMapping         |          |         | Mapping a LDAP group onto a S3App role `S3User` or `Admin`.                                                                             | AUTH_ROLES_MAPPING                                          |
| auth.sessionLifeTime      | 600      |         | Seconds of inactivity after which a user must re-login.                                                                                 | PERMANENT_SESSION_LIFETIME                                  |

### Authentication LDAP
| name                       | Default | Example                                         | Description                                                                                              | Config Parameter [(docu)](https://github.com/yotron/s3app/) |
|----------------------------|---------|-------------------------------------------------|----------------------------------------------------------------------------------------------------------|-------------------------------------------------------------|
| auth.ldap.server           |         | ldap://ldap.example.com                         | The URL of the LDAP server.                                                                              | AUTH_LDAP_SERVER                                            |
| auth.ldap.tls              |         | False                                           | If the LDAP server allows TLS secured communication set to True.                                         | AUTH_LDAP_USE_TLS                                           |
| auth.ldap.fields.firstname |         | givenName                                       | Name of the field of the person LDAP entity with the given name.                                         | AUTH_LDAP_FIRSTNAME_FIELD                                   |
| auth.ldap.fields.lastname  |         | sn                                              | Name of the field of the person LDAP entity with the last name.                                          | AUTH_LDAP_LASTNAME_FIELD                                    |
| auth.ldap.fields.email     |         | email                                           | Name of the field of the person LDAP entity with the email address.                                      | AUTH_LDAP_EMAIL_FIELD                                       |
| auth.ldap.fields.group     |         | memberOf                                        | When using AUTH_ROLES_MAPPING the name of the field with the role DN.                                    | AUTH_LDAP_GROUP_FIELD                                       |
| auth.ldap.fields.uid       |         | uid                                             | When using a LDAP search the field name with the username of the organizational unit.                    | AUTH_LDAP_UID_FIELD                                         |
| auth.ldap.usernameDN       |         | uid=%s,ou=users,dc=example,dc=com               | Distinguised name of the user to authenticate. `%s` will be replaced by the username of the S3App login. | AUTH_LDAP_USERNAME_FORMAT                                   |
| auth.ldap.domain           |         | example.com                                     | When a username always has a domain appendix.                                                            | AUTH_LDAP_APPEND_DOMAIN                                     |
| auth.ldap.search           |         | ou=users,dc=example,dc=com                      | LDAP search string if a user is part of an organizational unit.                                          | AUTH_LDAP_SEARCH                                            |
| auth.ldap.bind.user        |         | ldapadmin                                       | The bind user used for authentication against LDAP.                                                      | AUTH_LDAP_BIND_USER                                         |
| auth.ldap.bind.password    |         | myHiddenPassword                                | The password of the bin user sed for authentication against LDAP.                                        | AUTH_LDAP_BIND_PASSWORD                                     |
| auth.ldap.searchFilter     |         | (memberOf=cn=myTeam,ou=teams,dc=example,dc=com) | Filter the user which are allowed to access S3App generally.                                             | AUTH_LDAP_SEARCH_FILTER                                     |


You find further information about how to configure LDAP against Microsoft AD or OpenLDAP [here](https://flask-appbuilder.readthedocs.io/en/latest/security.html#authentication-ldap).

### TLS Parameter
| Name           | Default | Example              | Description                                                                                                                                                                                     |
|----------------|---------|----------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| tls.enabled    | false   |                      | Set to `true` to activate TLS termination (https) for the communication with S3App. Teh TLS setting is used for the Reverse Proxy and the Ingress Resource when active.                         |
| tls.secretName |         | defaultSelfSigned    | The secret name with the cert and key to use for TLS-termination.  You can define the secret externally (secret type `kubernetes.io/tls`or use the parameter `certs.tls` to create the secret.) |
| certs.tls      |         | see values.yaml file | Create a separated TLS cert and key pair with a name to allow TLS-termination with the Reverse Proxy or the Ingress Resources. Teh name is used in `tls.secretName`                             |

### Reverse Proxy Parameter
| Name                            | Default | Example | Description                                                  |
|---------------------------------|---------|---------|--------------------------------------------------------------|
| nginxproxy.enabled              | true    |         | Set to true to add a NGINX Reverse Proxy as a sidecar.       |
| nginxproxy.image                | nginx   |         | Name of the Docker image of the NGINX application.           |
| nginxproxy.tag                  | alpine  |         | Tag of the Docker image of the NGINX application to use      |
| nginxproxy.clientMaxBodySize    | 10m     |         | Set the max. size of the file to be uploaded.                |
| nginxproxy.clientConnectTimeout | 90      |         | Set the time out for idled connections in seconds.           |
| nginxproxy.proxySendTimeout     | 90      |         | Set the request time out during idling during send requests. |
| nginxproxy.proxyReadTimeout     | 90      |         | Set the request time out during idling of read requests.     |

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

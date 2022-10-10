



[![yotron](https://www.yotron.de/img/logo-yotron.png)](http://www.yotron.de)

[YOTRON](http://www.yotron.de) is a consultancy company which is focused on DevOps, Cloudmanagement and
Data Management with NOSQL and SQL-Databases. Visit us on [ www.yotron.de ](http://www.yotron.de)
ement with NOSQL and SQL-Databases. Visit us on www.yotron.de

# k8s-secrets

This HELM project organizes the provisioning of secrets in Kubernetes with [K8S secrets](https://kubernetes.io/docs/concepts/configuration/secret/). The project is safe to use. 
No applications are deployed, based purely on HELM functionality. 

You can deploy:
- TLS-Keys/Certs files, 
- basic username/passwords for databases or others,
- files like Java-TrustStores/KeyStores, 
- docker registries (to authenticate against your own DockerReg) simply with you url, name, password 

**We recommend using this Repo together with [helm-secrets](https://github.com/jkroepke/helm-secrets) to deploy secrets from you Vault**

**The secrets are available only for the K8S-namespace the HELM project was deployed to. If you need the secrets for different namespaces 
please deploy the project for every namespace.**

## prerequisites

- HELM 3

Binary files (e.g., Java KeyStores ) must be provided in their base64 encoded expression. To create a 
base64 encoded string of a file:

`cat <your file> | base64`

## integration
To integrate the Chart please add the HELM package to your dependencies:
```
dependencies:
  - name: k8s-secrets
    version: 1.0.0
    repository: http://helm.yotron.de/
```

## configuration
As a basic your `values.yaml` needs
```
k8s-secrets:
  ...
```
for the mapping of the secrets to the HELM Chart.

### setup dockerregistries
To add a docker registries you must define the repo and username/password for the docker registry. **No need to upload your complete json-syntax!**:
```
k8s-secrets:
  dockerregistries: # fixed name for this group
    - url: https://docker.artifactory.com/dockerhub # URL of you Docker registries
      name: <name to autheticate your regisitry> 
      password: <password to your regisitry> 
```

The secret itself is called `dockerregistries`.

To pull a Docker with the credentials you must add the `mydockerregistries` to your K8S manifest for the Pod-deployment.
Here is a snipped for an example to deploy a K8S-Pod with a container from a docker repo:
```
spec:
  imagePullSecrets:
    - name: mydockerregistries
  containers:
    - name: grafana
      image: https://docker.artifactory.com/dockerhub/grafana/grafana:latest
```

### setup secretplain
Setup default secrets which are provided as plaintext.
```
k8s-secrets:
  secretplain: # fixed name for this group
    ppadmin: # free name of the secret in K8S
      name: admin
      password: mypasswordinplaintext
```

### setup secretbase64
Setup default secrets which are provided in their base63 encoded expression. This is suitable for binaries.
```
k8s-secrets:
  secretbase64: # fixed name for this group
    myjavakeystruststore: # free name of the secret in K8S
      keystore.jks: YXNjYWNhc2N.....hc2Nhc2Nhc2Nhc2Nhc2M=
      truststore.jks: YXNjYXNjYXNj....YXNjYXNjYXNjYXNjYXNjYXNj
```

### setup basic with username and password
The group basic contains basic-authentication secrets with username and password.

```
k8s-secrets:
  basic: # fixed name for this group
    cloudpgdb: # free name of the secret in K8S
      username: db1
      userpassword: mypasswordinplaintext
```

How to add secrets to your deployment of K8S [Link](https://kubernetes.io/docs/tasks/inject-data-application/distribute-credentials-secure/)

### setup tls
The group tls contains tls secrets of K8S with key and cert.
```
k8s-secrets:
  tls: # fixed name for this group
    druidtls: # free name of the tls secret in K8S. 
      crt: mycertinplaintext
      key: mykeyinplaintext
```

How to add secrets to your deployment of K8S [Link](https://kubernetes.io/docs/tasks/inject-data-application/distribute-credentials-secure/)

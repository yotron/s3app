[![yotron](https://www.yotron.de/img/logo-yotron.png)](http://www.yotron.de)

[YOTRON](http://www.yotron.de) is a consultancy company which is focused on DevOps, Cloudmanagement and
Data Management with NOSQL and SQL-Databases. Visit us on [www.yotron.de](http://www.yotron.de)
ement with NOSQL and SQL-Databases.

# S3App
S3 (Simple Storage Solution) is a file storage services which is part of Cloud solutions. It is known for its
scalability, data availability, security, performance and the ease to connect storage clients to it. Introduced by Amazon in AWS, other
provider of managed S3 are available just like software solutions to set up an private S3-solution like ([Ceph](https://ceph.io/) or [Cloudian](https://cloudian.com/)).

**S3App simplifies** the access to a S3Buckets with a provider independent web based frontend which allows
the visualizing and the management of the content of S3 buckets with an S3 provider independent web application, ....

For further information and the manual, please see [s3app/manual](http://192.168.56.105:1313/s3app/manual/)

## S3App URLs
The project contains code, build packages, container ... . Below an overview:

| Type                  | Provider                        | URL                                                           |
|-----------------------|---------------------------------|---------------------------------------------------------------|
| S3App Manual          | yotron.de                       | http://www.yotron.de/s3app/                                   |
| Container             | hub.docker.com                  | https://hub.docker.com/repository/docker/yotronpublic/s3app   | 
| Python Package (PyPi) | pypi.org                        | https://pypi.org/project/s3app/                               |  
| HELM package          | artifacthub.io / helm.yotron.de | https://artifacthub.io/packages/helm/yotron-helm-charts/s3app |
| Code/Contribution     | github.com                      | https://github.com/yotron/s3app/                              |
| Problems/Feedback     | github.com                      | https://github.com/yotron/s3app/issues                        |

## Installation
We provide two installation methods. A native installation on any OS which supports Python3 and a installation in Kubernetes via HELM.
Per default, S3App runs on a sqlite database. Sqlite is recommended only for testing and on a standalone installation.

In production, you should use a PostgreSQL database for a better data persistency and to allow a HA setup with more S3App nodes.

The S3App has no TLS-termination ("https"). We recommend to use a Reverse Proxy like NGINX or Apache Web Server in front of S3App Web App for TLS termination.

The HELM project of S3App for Kubernetes contains all needed and recommended components. You can optionally install a NGINX Reverse Proxy and a PostgreSQL database with the project,
but you can also use separated applications.

### Native
#### Prerequisites
- [Python3](https://www.python.org/)
- [Python-pip](https://pip.pypa.io) for dependency installation
- recommended: python3-venv to create a virtual environment for Python3
- recommended: [PostgreSQL](https://www.postgresql.org/) database for the S3App metadata
- recommended: A reverse proxy with TLS termination (e.g. NGINX).

S3App supports all current Python3 versions. It is tested with Python 3.9.x and 3.10.x

To check which Python version is running:
```
vagrant@bullseye:~$ python3 -V
Python 3.9.2
``` 
To check which Pip version is running:
``` 
vagrant@bullseye:~$ pip3 -V
pip 20.3.4 from /home/vagrant/s3app/lib/python3.9/site-packages/pip (python 3.9)
``` 

It is possible, that in your distribution Python must be called with `python` and `pip`.

If you need a Python installation from the scratch. Python3, Pip3 and python3-venv are available in the main OS distribution.

For Debian/Ubuntu:
`sudo apt-get install python3 python3-pip python3-venv`

For CentOS:
`sudo yum install python3 python3-pip python3-venv`


#### Installation
There are a lot of variants how to start a Python web project. We use a Python virtual environment for setting up S3App on a virtual environment. 
Depend on your environment and knowledge in Python the process can be different.

1. Create a virtual environment of Python
 
   1. Create a virtual environment for S3App
   
      ```
      vagrant@bullseye:~$ python3 -m venv venv
      ```

   2. Activate your virtual environment

      This steps is to repeat every time you want to restart S3App.
   
      ```
      vagrant@bullseye:~$ source venv/bin/activate
      (venv) vagrant@bullseye:~$
      ```

3. Install all Python dependencies needed for the project:

   ```   
   (s3app) vagrant@bullseye:~$ pip install s3app --upgrade
   ```

4. Start S3App server
   ```   
   (s3app) vagrant@bullseye:~$ s3app-run --host=0.0.0.0 --port=8080
   The APP is running in DEBUG mode.
   2022-10-06 15:21:07,382:INFO:flask_appbuilder.base:Registering class S3View on menu 
   2022-10-06 15:21:07,383:INFO:flask_appbuilder.baseviews:Registering route /s3/<string:prefixUrl> ('GET',)
   2022-10-06 15:21:07,383:INFO:flask_appbuilder.baseviews:Registering route /s3/ ('GET',)
   ...
   2022-10-10 11:18:22,384:INFO:flask_appbuilder.base:Registering class S3View on menu 
   2022-10-10 11:18:22,385:WARNING:flask_appbuilder.base:View already exists S3View ignoring
   2022-10-10 11:18:22,385:INFO:flask_appbuilder.base:Registering class S3IndexView on menu
   2022-10-10 11:18:22,385:INFO:flask_appbuilder.baseviews:Registering route / ('GET',)
   2022-10-10 11:18:22,424:INFO:waitress:Serving on http://0.0.0.0:8080
   ```

4. Open Browser and start S3App with one of the IPs mentioned above:

   ![Login Site of S3Maanger.png](s3app.png)

   Your will automatically redirected to http://x.x.x.x:8080/login

5. Login as a admin user
   
   The default credentials for the admin user are:
 
   **Username**: admin

   **Password**: admin

   ![Dashboard of S3App](s3appdashboard.png)

### HELM
You find the installation instructions for Kubernetes [here](https://artifacthub.io/packages/helm/yotron-helm-charts/s3app)

## Manual
The manual for S3App you find [here](http://www.yotron.de/s3app/)

## Configuration
### The dotenv file and `S3APP_CONF_FILE` variable
You can customize S3App with a few parameters. All parameters must be set in a config file with a name like `.s3app`. The name can be chosen freely and you can put the file in a folder of your choice but 
the file must be reachable by the S3App App. 

Additionally, you need a environment variable `S3APP_CONF_FILE` with the path to your config file.

For example, for Linux you can set the environment variable with:
```
export S3APP_CONF_FILE=/etc/s3app/.s3app
```

The config file can contain the following parameters:

```
S3APP_APP_NAME = "My Fancy S3 App"
S3APP_APP_ICON = "https://myserver.com/my_own_logo.svg"
S3APP_LOG_LEVEL = "debug"
S3APP_LOG_FILE = ./s3app.log 
S3APP_DB_TYPE = "postgresql"
S3APP_PG_DB_HOST = "k8s-1"
S3APP_PG_DB_NAME = "s3app"
S3APP_PG_DB_PORT = 5432
S3APP_PG_DB_USER_PW = "s3app"
S3APP_PG_DB_USER_NAME = "s3app"
S3APP_SECRET_KEY = "thisIsMyHiddenSecretKey"
```

### The parameter of the config file
| name                  | example                              | description                                                                                                            | possible values                    | default |
|-----------------------|--------------------------------------|------------------------------------------------------------------------------------------------------------------------|------------------------------------|---------|
| S3APP_APP_NAME        | My Fancy S3 App                      | The name of your S3App. It is display in the head of your application.                                                 |                                    |         |
| S3APP_APP_ICON        | https://myserver.com/my_own_logo.svg | The icon of your S3App as a html link. It is display in the head of your application.                                  |                                    |         |
| S3APP_LOG_LEVEL       | info                                 | LogLevel for the Logging.                                                                                              | fatal, error, warning, info, debug | info    |
| S3APP_LOG_FILE        | /var/log/s3app.log                   | When set logs are written to the mentioned file. If not set it is written to console (stdout).                         |                                    | not set |
| S3APP_DB_TYPE         | postgresql                           | Type of database to use. Can be a SQLite or a PostgreSQL Database                                                      | sqlite, postgres                   | sqlite  |
| S3APP_PG_DB_HOST      | k8s-1.mydatabse.com                  | Only if db-type postgres: Host name of the PostresSQL server.                                                          |                                    |         |
| S3APP_PG_DB_PORT      | 5432                                 | Only if db-type postgres: Port number of the PostresSQL server.                                                        |                                    | 5432    |
| S3APP_PG_DB_NAME      | s3app                                | Only if db-type postgres: Name of the PostgreSQL Database.                                                             |                                    |         |
| S3APP_PG_DB_USER_NAME | s3app                                | Only if db-type postgres: Username to authenticate against the PostgreSQL Database                                     |                                    |         |                      
| S3APP_PG_DB_USER_PW   | s3app                                | Only if db-type postgres: Password to authenticate against the PostgreSQL Database                                     |                                    |         |
| S3APP_SECRET_KEY      | thisIsMyHiddenSecretKey              | A key which used to sign session cookies for protection against cookie data tampering. In production please change it. |                                    |         |

## The start parameter
To start of the S3App server simply call `s3app-run` as shown above. You have has the following parameter:

| name     | short        | example   | description                            | default   |
|----------|--------------|-----------|----------------------------------------|-----------|
| HOST     | -s, --host   | 127.0.0.1 | Listener Host IP. 0.0.0.0 for all IPs. | 0.0.0.0   |
| PORT     | -P, --port   | 8090      | Listener Host Port                     | 8080      |
| THREADS  | -t --threads | 1         | Threads for parallelization            | 4         |

With `s3app-run -h` you get the possible configuration: 

```
(s3app) vagrant@bullseye:~$ s3app-run -h
...
usage: s3app-run [-h] [-s HOST] [-p PORT] [-t THREADS]
Start parameter for the S3App web server.
optional arguments:
-h, --help            show this help message and exit
-s HOST, --host HOST  Listener Host IP. Default: 0.0.0.0
-p PORT, --port PORT  Listener Host Port. Default: 8080.
-t THREADS, --threads THREADS  Threads for parallelization. Default: 4.
```
   
# Cloud Analysis Manager

## Run Configuration

### Env Variables

| ENV                    | Default                         | Description                                                                               |
|------------------------|---------------------------------|-------------------------------------------------------------------------------------------|
| DJANGO_SETTINGS_MODULE | cloud_analysis_manager.settings | Django settings path. NOTE: This will need to be set through PyCharm's run configuration. |
| DB_USER                |                                 | Database User                                                                             |
| DB_PASSWORD            |                                 | Database Password                                                                         |
| DB_HOST                |                                 | Database Host                                                                             |
| DB_PORT                |                                 | Database Port                                                                             |

The [.env](cloud_analysis_manager/.env) file can be used to set necessary environment variables.

## PostgreSQL Database

Download and install [PostgreSQL](https://www.postgresql.org/download/). I have been using version 11, although version 12 should work.

The ```cloud_analysis_manager``` database will need to be manually created when the project is initially cloned.

```
CREATE DATABASE cloud_analysis_manager
```

### Manually Upgrading DB

1. Run ```python manage.py makemigrations``` to make the migration scripts
2. Run ```python manage.py migrate``` to apply the migration scripts

### Seeding the DB

There is a json file with some fixture data. This can be used to seed the db.

```
python manage.py loaddata seed.json
```

## Django-Admin

Accessing the django admin locally can be done so at http://127.0.0.1:8000/admin/. 
A user will need to be created who can login to the admin site.

```
python manage.py createsuperuser
```

## Ansible

There are some parts of this project that uses ansible. If ansible is not installing, then commenting out the following may be necessary:
* In requirements.txt
    * ansible==2.9.1
    * ansible-runner==1.4.4
* In app/views.py
    * any reference to the ```run_playbook``` command

## Uploading docker image to GCP

```docker tag dummy-engine gcr.io/mmars-test/dummy-engine:latest```

```docker push gcr.io/mmars-test/dummy-engine:latest```

## Getting docker up and running

You can install Docker for windows [here](https://hub.docker.com/editions/community/docker-ce-desktop-windows/). Once it is installed, you need to go to the start menu and get it run as an administrator. Right Click on the Docker icon and open settings. We need to change the settings to be able to use Docker on developer machine. Do the following changes
1. Go to Resources --> File Sharing and add your cloud_analysis_manager folder location here. 
2. Go to General and make sure that "Expose daemon on tcp://localhost:2375 without TLS" is enabled
3. Go to power shell and run the following

   ``` $env:DOCKER_HOST="tcp://0.0.0.0:2375" ```

   This step might not be required always. See if you can do away without it. To check you should go the cloud_analysis_manager repository folder through powershell and run docker

4. Navigate to the folder location or use your pycharm terminal (make sure to be in folder cloud_analysis_manager where DockerFile sits) and run 

   ``` docker-compose up ```  

## Grafana configuration

When you run pip install for this project, grafana will be setup. In order for it to run with our project, we need to,
1. Hit http://127.0.0.1:3000/ on the browser
2. Login with default username and password 
   
   ```Username: admin```
   ```Password: admin``` 
   
   You will then be prompted to change the password. Do so.
3. Once logged in, go to ```Configuration``` from the left hand side bar and add a new API key. Once a new key is added, you will be given an API key in return. Note this key and add it to your .env file against ```GRAFANA_API_KEY```
4. Make sure your .env file contains the following value too
   ```GRAFANA_TEMPLATE=static/dashboard.json``` 
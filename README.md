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

A user will need to be created who can login to the admin site (e.g. http://localhost/admin).

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

Mitchell was here
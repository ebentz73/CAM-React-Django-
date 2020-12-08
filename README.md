# Cloud Analysis Manager

## Configuration

### Env Variables

| ENV                    | Default                         | Description                                                                               |
|------------------------|---------------------------------|-------------------------------------------------------------------------------------------|
| DJANGO_SETTINGS_MODULE | cloud_analysis_manager.settings | Django settings path. NOTE: This will need to be set through PyCharm's run configuration. |
| DB_USER                |                                 | PostgreSQL User                                                                           |
| DB_PASSWORD            |                                 | PostgreSQL Password                                                                       |
| DB_HOST                |                                 | PostgreSQL Host                                                                           |
| DB_PORT                |                                 | PostgreSQL Port                                                                           |
| EVAL_ENGINE_IMAGE      | lonestar/trunavcore:latest      | The eval engine docker image.                                                             |
| POWERBI_CLIENT_ID      |                                 | Azure service principal client id.                                                        |
| POWERBI_CLIENT_SECRET  |                                 | Azure service principal client secret.                                                    |
| POWERBI_TENANT_ID      |                                 | Azure service principal tenant id.                                                        |

The `cloud_analysis_manager/.env` file can created to set necessary environment variables. It is ignored by git.

### Endpoints

The following is not a complete list of endpoints, just the ones I deem most people should care about.

`/frontend-app/home/`

The home page of the frontend. The following frontend urls can be accessed through navigating the pages from here.

`/frontend-app/solution/<solution-id>/scenario/`

Gives a list of scenarios for the solution that you can pick to view.

`/frontend-app/solution/<solution-id>/scenario/<scenario-id>/`

View the given scenario that is within to the solution.

`/frontend-app/solution/<solution-id>/new-scenario/`

Create a new scenario within given solution.

## PostgreSQL Database

Download and install [PostgreSQL](https://www.postgresql.org/download/). I have been using version 11, although version 12 should work.

The `cloud_analysis_manager` database will need to be manually created when the project is initially cloned.

```postgresql
CREATE DATABASE cloud_analysis_manager
```

### Manually Upgrading DB

1. Run `python manage.py makemigrations` to make the migration scripts
2. Run `python manage.py migrate` to apply the migration scripts

## Django-Admin

Accessing the django admin locally can be done so at http://127.0.0.1:8000/admin/.
A user will need to be created who can login to the admin site.

```bash
python manage.py createsuperuser
```

## Getting docker up and running

You can install Docker for windows [here](https://hub.docker.com/editions/community/docker-ce-desktop-windows/). Once it is installed, you need to go to the start menu and get it run as an administrator. Right Click on the Docker icon and open settings. We need to change the settings to be able to use Docker on developer machine. Do the following changes

1. Go to Resources --> File Sharing and add your cloud_analysis_manager folder location here.
2. Go to General and make sure that "Expose daemon on tcp://localhost:2375 without TLS" is enabled.
3. Go to power shell and run `$env:DOCKER_HOST="tcp://0.0.0.0:2375"`.

   Note: This step might not always be required. To check, open this repository in powershell and run docker.

4. Navigate to the folder location or use your pycharm terminal (make sure to be in folder cloud_analysis_manager where DockerFile sits) and run `docker-compose up`

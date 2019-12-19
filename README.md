# Cloud Analysis Manager

## DB Upgrade

The ```cloud_analysis_manager``` database will need to be manually created when the project is initially created.
This only needs to be done once.

```CREATE DATABASE cloud_analysis_manager```

### Manually Upgrading DB

1. Run ```python manage.py makemigrations``` to make the migration scripts
2. Run ```python manage.py migrate``` to apply the migrations

## Adding A New Input

The places that need to be updated are
* app.admin
* app.models

## Uploading docker image to GCP

```docker tag dummy-engine gcr.io/mmars-test/dummy-engine:latest```
```docker push gcr.io/mmars-test/dummy-engine:latest```

Mitchell was here
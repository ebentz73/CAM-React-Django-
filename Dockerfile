# pull official base image
FROM python:3.8.0

# set work directory
WORKDIR /code

# set environment variables
ENV PYTHONUNBUFFERED 1

# install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# install frontend app dependencies
RUN apt-get install nodejs

# copy project
COPY . .
RUN chmod +x docker-entrypoint.sh
ENTRYPOINT ["./docker-entrypoint.sh"]
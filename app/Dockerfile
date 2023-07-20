# pull official base image
FROM python:3.10-slim

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV HOME=/home/app
ENV APP_HOME=/home/app/web

# create directory for the app user
RUN mkdir -p $HOME
# and then create the app user
RUN addgroup --system app && adduser --system --ingroup app app

# create authorized directory for app user and make it as workdir
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/staticfiles
RUN mkdir $APP_HOME/mediafiles
WORKDIR $APP_HOME

# install dependencies for linux
#RUN apt-get update
#RUN apt-get -y install libpq-dev gcc
RUN apt-get update \
    && apt-get install -y libpq-dev gcc python3-dev

# install dependencies for python
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .

# chown all the files to the app user
RUN chown -R app:app $APP_HOME

# change to the app user
USER app


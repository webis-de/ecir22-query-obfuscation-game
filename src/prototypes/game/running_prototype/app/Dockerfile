FROM python:3.7

RUN apt-get update \
  && apt-get install -y openjdk-11-jdk

COPY . /app

WORKDIR /app

RUN pip3 install --no-dependencies -r requirements.txt

ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64/
ENV FLASK_APP=flask_server


FROM dancastellani/adrf-python2:1.0

ENV PYTHONUNBUFFERED 1
ENV CODACY_PROJECT_TOKEN 6aefb79c080240aeba2c4ac1e13428e8

RUN mkdir /code
WORKDIR /code
ADD . /code/

#RUN apt-get update -y && apt-get install -y $(grep -vE "^\s*#" apt-get.txt | tr "\n" " ")
#RUN echo America/New_York | tee /etc/timezone && dpkg-reconfigure --frontend noninteractive tzdata
RUN apt-get update -y && apt-get install -y git

RUN mkdir -p /var/log/django/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install -r test-requirements.txt

LABEL maintainer="Daniel.Castellani@nyu.edu"

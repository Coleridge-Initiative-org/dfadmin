FROM dancastellani/adrf-python2:1.1

ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get upgrade -y && apt dist-upgrade -y && apt-get install -y git

#RUN apt-get update -y && apt-get install -y $(grep -vE "^\s*#" apt-get.txt | tr "\n" " ")
#RUN echo America/New_York | tee /etc/timezone && dpkg-reconfigure --frontend noninteractive tzdata

RUN mkdir /code
WORKDIR /code
ADD . /code/

RUN mkdir -p /var/log/django/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install -r test-requirements.txt

LABEL maintainer="Daniel.Castellani@nyu.edu"



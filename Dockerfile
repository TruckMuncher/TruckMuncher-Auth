FROM ubuntu:14.04
MAINTAINER Josh Ault <josh.ault3@gmail.com>

RUN apt-get update -qq && apt-get install -y git-core
RUN apt-get install -y python-software-properties python-pip
ADD . /opt/TruckMuncher-Auth
WORKDIR /opt/TruckMuncher-Auth
RUN pip install -r requirements.txt

EXPOSE 5000

CMD python auth.py

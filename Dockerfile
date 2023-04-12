FROM ubuntu:latest
RUN apt-get update -y
RUN apt-get install python3 -y
RUN apt-get install python3-pip -y
WORKDIR /dochub
COPY ./requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# install dependencies
COPY . .

# copy project

EXPOSE 8000
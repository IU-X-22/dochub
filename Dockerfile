FROM ubuntu:latest

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update -y
RUN apt-get install python3 python3-pip poppler-utils git -y
RUN pip3 install --upgrade pip


WORKDIR /dochub

COPY ./requirements.txt ./requirements.txt
RUN pip install  -r requirements.txt --no-cache-dir

COPY . .

EXPOSE 8000
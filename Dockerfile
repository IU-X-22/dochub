FROM ubuntu:latest

RUN apt-get update -y
RUN apt-get install python3 python3-pip poppler-utils -y

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /dochub
COPY . .

RUN pip3 install -r requirements.txt

EXPOSE 8000
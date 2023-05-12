FROM ubuntu:latest

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update -y
RUN apt-get install python3 python3-pip poppler-utils git -y

RUN pip install easyocr

COPY ./requirements.txt ./requirements.txt
RUN pip install  -r requirements.txt 

RUN rm /requirements.txt

RUN groupadd -r moderator && useradd --no-log-init -m -r -g moderator moderator

WORKDIR /home/moderator/

RUN chown -R moderator /home/moderator/
COPY . .
RUN chmod -R 777 /home/moderator/

USER moderator

EXPOSE 8000
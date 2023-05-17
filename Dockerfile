FROM ubuntu

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update -y
RUN apt-get install python3 python3-pip poppler-utils git gunicorn -y

RUN pip install  --no-cache-dir easyocr

COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt 

RUN rm /requirements.txt


RUN groupadd -r moderator && useradd --no-log-init -m -r -g moderator moderator

RUN pip install pytz --upgrade
RUN pip install tzdata --upgrade

WORKDIR /home/moderator/

RUN chown -R moderator /home/moderator/
COPY . .


RUN chmod -R 777 /home/moderator/

USER moderator

EXPOSE 8000
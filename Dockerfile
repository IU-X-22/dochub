FROM python:latest

WORKDIR .
RUN sudo apt update && sudo apt upgrade

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# install dependencies

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt
# copy project
COPY . .
RUN python3 manage.py makemigrations
RUN python3 manage.py migrate --run-syncdb
CMD ["python3","manage.py","runserver","0.0.0.0:8000"]
EXPOSE 8000
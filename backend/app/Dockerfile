FROM python:3.8
ENV PYTHONBURRERED=1
WORKDIR /django
COPY requirements.txt requirements.txt

RUN apt-get update && apt-get upgrade -y

RUN pip3 install -r requirements.txt

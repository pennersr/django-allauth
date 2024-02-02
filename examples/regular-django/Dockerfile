FROM python:3.12
ENV PYTHONUNBUFFERED 1

# Needed for SAML support
RUN  apt-get update
RUN  apt-get -y install libxml2-dev libxmlsec1-dev libxmlsec1-openssl

WORKDIR /code/
COPY requirements.txt \
    manage.py \
    Makefile \
    ./
RUN pip install -r requirements.txt
COPY ./example ./example/
EXPOSE 8000

FROM ubuntu:20.04

ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y software-properties-common \
    && add-apt-repository -y ppa:deadsnakes/ppa \
    && apt-get install -y python3.5 \
	  python3.6 \
	  python3.7 \
	  python3.8 \
	  python3.9 \
	  python3-pip \
	  && python3.9 -m pip install --upgrade pip \
	  && pip3 install tox \
	  && apt-get install -y nodejs \
	  npm \
	  && apt-get autoremove \
	  && rm -rf /var/lib/apt/lists/*

WORKDIR /django-allauth
COPY . /django-allauth

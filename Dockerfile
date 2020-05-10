FROM floydhub/python-base:latest-gpu-py3

MAINTAINER "Antonio De Marinis" <demarinis@eea.europa.eu>

ADD ./src/eea.corpus/requirements.txt /src/eea.corpus/requirements.txt

WORKDIR /src/eea.corpus

RUN pip --no-cache-dir install -U -r r
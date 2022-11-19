#FROM alpine:3.10
# RUN apk add --no-cache python3-dev \
#     && pip3 install --upgrade pip
FROM ubuntu:latest

RUN set -xe \
    && apt-get update \
    && apt-get install python3-pip -y
RUN pip install --upgrade pip

COPY main.py /bots/
COPY requirements.txt /tmp
COPY .env /bots/

RUN pip3 install -r /tmp/requirements.txt

WORKDIR /bots

CMD ["python3", "main.py"]
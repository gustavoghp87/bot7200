FROM alpine:3.10

RUN apk add --no-cache python3-dev \
    && pip3 install --upgrade pip

COPY main.py /bots/
COPY requirements.txt /tmp
COPY .env /bots/

RUN pip3 install -r /tmp/requirements.txt

ARG VERSION=96.0.4664.110-0ubuntu0.18.04.1
ARG ARCH=arm64
ARG URLBASE=https://launchpad.net/~canonical-chromium-builds/+archive/ubuntu/stage/+files

WORKDIR /opt/chromium

RUN wget ${URLBASE}/chromium-codecs-ffmpeg_${VERSION}_${ARCH}.deb \
 && wget ${URLBASE}/chromium-codecs-ffmpeg-extra_${VERSION}_${ARCH}.deb \
 && wget ${URLBASE}/chromium-browser_${VERSION}_${ARCH}.deb \
 && wget ${URLBASE}/chromium-chromedriver_${VERSION}_${ARCH}.deb \
 && apt-get update \
 && apt-get install -y ./chromium-codecs-ffmpeg_${VERSION}_${ARCH}.deb \
 && apt-get install -y ./chromium-codecs-ffmpeg-extra_${VERSION}_${ARCH}.deb \
 && apt-get install -y ./chromium-browser_${VERSION}_${ARCH}.deb \
 && apt-get install -y ./chromium-chromedriver_${VERSION}_${ARCH}.deb \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip \
 && pip install selenium

WORKDIR /bots

CMD ["python3", "main.py"]
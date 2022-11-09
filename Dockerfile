FROM python:3-slim-buster

RUN  apt-get -y update
RUN apt-get install -y gcc python3-dev python3-rpi.gpio

RUN pip install RPi.GPIO
COPY fan_ctrl.py /app/

WORKDIR /app
COPY docker-entrypoint.sh /app/docker-entrypoint.sh

CMD ["./docker-entrypoint.sh"]
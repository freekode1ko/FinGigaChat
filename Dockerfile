FROM python:3.8-slim

RUN mkdir /fingigachat

RUN mkdir /fingigachat/module

RUN mkdir /fingigachat/source

RUN mkdir /fingigachat/source/img

RUN mkdir /fingigachat/source/tables

ENV TZ="Europe/Moscow"

COPY requirements.txt /fingigachat

RUN pip3 install --upgrade pip setuptools setuptools_rust && pip3 install -r fingigachat/requirements.txt

COPY corntab_fingigachat /fingigachat

RUN apt-get update && apt-get -y install cron

RUN touch /var/log/fingigachat.log && chmod 777 fingigachat/corntab_fingigachat && crontab fingigachat/corntab_fingigachat

COPY ./app /fingigachat

WORKDIR /fingigachat

CMD printenv | grep -v "no_proxy" >> /etc/environment && cron -f

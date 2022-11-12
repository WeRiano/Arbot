FROM python:3.11.0-alpine3.16

WORKDIR /app

ADD . /app

RUN apk add python3-dev build-base linux-headers pcre-dev
RUN pip install -r requirements.txt

CMD ["uwsgi", "uwsgi.ini"]
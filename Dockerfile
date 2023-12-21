FROM python:3-alpine3.15

WORKDIR /app

COPY . /app

EXPOSE 3000

CMD python ./application.py


FROM python:3.11

WORKDIR /app

COPY . /app

RUN pip isntall -r requirements.txt

EXPOSE 3000

CMD python ./application.py
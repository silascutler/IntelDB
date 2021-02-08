FROM python:3

RUN apt update
RUN apt install -y python3-mysqldb

RUN pip install pymongo
RUN pip install ConfigParser
RUN pip install requests
RUN pip install flask
RUN pip install mysqlclient

COPY . /app

CMD python -u /app/main.py
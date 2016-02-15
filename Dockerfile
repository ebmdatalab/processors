FROM python:2.7
WORKDIR /service
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY warehouse warehouse
FROM python:3.10

COPY requirements.txt /tmp/requirements.txt

RUN python3 -m pip install --upgrade pip

RUN python3 -m pip install -r /tmp/requirements.txt

WORKDIR /app
COPY . .

RUN python project/main.py


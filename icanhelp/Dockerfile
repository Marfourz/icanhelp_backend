FROM python:3

ENV PYTHONBUFFERD 1

ENV PYTHONDONTWRITEBYTECODE 1

RUN mkdir /app

WORKDIR /app

COPY . /app/

COPY entrypoint.sh /app/entrypoint.sh

RUN python -m venv /env

ENV PATH="/env/bin/:$PATH"

RUN python -m pip install --upgrade pip 

COPY requirements.txt /app/

RUN pip install -r requirements.txt





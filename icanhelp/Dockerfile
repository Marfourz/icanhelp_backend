FROM python:3

ENV PYTHONBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN mkdir /app
WORKDIR /app

RUN python -m venv /env
ENV PATH="/env/bin/:$PATH"

RUN python -m pip install --upgrade pip

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY . /app/                          
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh


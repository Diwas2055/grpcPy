FROM python:3.10-slim

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

COPY ./app.py /app/app.py

RUN pip install -r requirements.txt

CMD [ "python", "app.py" ]
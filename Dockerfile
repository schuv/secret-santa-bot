FROM python:3.9

COPY .env .
COPY requirements.txt .
COPY ./src/ .

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -r requirements.txt

CMD ["python3", "app.py"]
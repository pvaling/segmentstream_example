FROM python:3.6

WORKDIR /app
COPY requirements.txt .

RUN pip install -r requirements.txt
COPY . .
#VOLUME /usr/local/lib/python3.6 /usr/local/lib/python3.6

CMD ["python","app.py"]
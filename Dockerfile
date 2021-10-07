FROM python:3.8-slim-buster AS build

WORKDIR /app

COPY . .
RUN pip3 install -r requirements.txt

CMD ["--help"]

ENTRYPOINT ["python3", "/app/db-archive.py"]

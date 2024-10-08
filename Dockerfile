FROM python:3.13-slim

WORKDIR /app

RUN apt update && apt install -y curl gnupg && \
    echo "deb http://apt.postgresql.org/pub/repos/apt/ buster-pgdg main" >>  /etc/apt/sources.list.d/pgdg.list && \
    curl https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - && \
    apt install -y mariadb-client postgresql-client

COPY . .
RUN pip3 install -r requirements.txt

CMD ["--help"]

ENTRYPOINT ["python3", "/app/db-archive.py"]

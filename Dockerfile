FROM python:3.13.0b1-slim-bookworm

WORKDIR /app
COPY ./requirements.txt .
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt
COPY . ./

RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]


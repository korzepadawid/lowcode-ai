FROM python:3.10-alpine as base
RUN apk add --update --virtual .build-deps \
    build-base \
    postgresql-dev \
    python3-dev \
    libpq

COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

FROM python:3.10-alpine
RUN apk add libpq
COPY --from=base /usr/local/lib/python3.10/site-packages/ /usr/local/lib/python3.10/site-packages/
COPY --from=base /usr/local/bin/ /usr/local/bin/
COPY . /app
ENV PYTHONUNBUFFERED 1
ENV DEBUG 0
WORKDIR /app
EXPOSE 8000
RUN ls -l entrypoint.sh
RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]

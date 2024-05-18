FROM tiangolo/uvicorn-gunicorn:python3.11-slim

WORKDIR /app
COPY ./requirements.txt .
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt
COPY . ./

RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]


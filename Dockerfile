#
FROM python:3.9

#
WORKDIR /app

#
COPY ./requirements.txt /code/requirements.txt

#
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

#
COPY . /code/app

WORKDIR /code/app

#
CMD ["uvicorn", "--host", "0.0.0.0", "main:app"]

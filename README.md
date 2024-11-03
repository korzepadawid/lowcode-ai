# lowcode-ai

## How to run?

Create and activate a [virtual environment](https://docs.python.org/3/library/venv.html).


```
$ pip install -r requirements.txt
```

```
$ uvicorn main:app --reload --log-level debug
```

## How to run a database locally?

```
$ make initdb
```

## How to remove a database locally?

```
$ make rmdb
```

# How to run on a local setup?

```
$ make dev
```

# How to run with docker?

Prepare a `.env` file:
```
DATABASE_USER=
DATABASE_PASSWORD=
DATABASE_HOST=
DATABASE_NAME=
DATABASE_PORT=
OPENAI_API_KEY=
OPENAI_PROJECT_ID=
```

```
$ docker run -p8000:8000 --env-file .env_example ghcr.io/korzepadawid/lowcode-ai:latest
```

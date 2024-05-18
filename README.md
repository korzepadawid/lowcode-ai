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
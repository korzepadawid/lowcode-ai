import logging

from fastapi import FastAPI

log = logging.getLogger('uvicorn.error')
app = FastAPI()


@app.get("/")
def read_root():
    log.debug("Hello world log!")
    return {"Hello": "World"}
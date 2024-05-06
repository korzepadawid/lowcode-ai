import logging

from fastapi import FastAPI

from app.api.endpoints.threads import router as threads_router
from app.models import Thread

log = logging.getLogger('uvicorn.error')
app = FastAPI()
app.include_router(threads_router)

@app.get("/")
def read_root():
    log.debug("Hello world log!")
    return {"Hello": "World"}
import logging

from fastapi import FastAPI

from app.api.endpoints.threads import router as threads_router

log = logging.getLogger('uvicorn.error')
app = FastAPI()
app.include_router(threads_router)

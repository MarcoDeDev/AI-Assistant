from fastapi import FastAPI
from app.api.router import api_router
import app.core.logging
from app.core.exception_handlers import (
    register_exception_handlers,
)


app = FastAPI()

register_exception_handlers(app)

app.include_router(api_router)
from fastapi import FastAPI
from app.api.router import api_router
import app.core.logging


app = FastAPI()

app.include_router(api_router)
# main.py
from fastapi import FastAPI
from routes.api import api_router

app = FastAPI()

app.include_router(api_router)

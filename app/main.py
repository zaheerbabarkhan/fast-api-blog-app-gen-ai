from fastapi import FastAPI
from core.db import get_db

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}
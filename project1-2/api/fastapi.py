from dotenv import load_dotenv
from fastapi import FastAPI
import os

load_dotenv()
app = FastAPI()

@app.get("/")
def read_root():
    app_name = os.getenv("APP_NAME", "project1-2")
    return {"message": f"Hello from {app_name}!"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}
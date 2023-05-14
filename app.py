from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class Message(BaseModel):
    message_id: int
    from_user: Optional[dict] = None
    date: int
    text: str

@app.post("/webhook")
async def read_message(message: Message):
    print(f"Received message from {message.from_user} with text {message.text}")
    return {"received": True}

@app.post("/message")
async def read_message(message):
    print(f"RECEIVED MESSAGE WHICH IS:")
    print(message)
    return {"received": True}

@app.get("/test")
async def test_api():
    return {"message": "API works!"}

@app.get("/message")
async def test_api():
    return {"message": "API works!"}
import uvicorn

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8005, log_level="info")
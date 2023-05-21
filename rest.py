from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI

from genie.config import Locations
from genie.indexing import Index
import uvicorn

load_dotenv()
base = Path(".")
locations = Locations(base)
index = Index(locations, "gpt-4")

from typing import List
from pydantic import BaseModel


class Dialog(BaseModel):
    message: str
    dialog_messages: List[str]

class ResponseModel(BaseModel):
    answer: str
    n_input_tokens: int
    n_output_tokens: int
    n_first_dialog_messages_removed: int
    error: bool

app = FastAPI()

@app.post("/message", response_model=ResponseModel)
async def receive_dialog(dialog: Dialog):
    message = str(dialog.message)
    n_input_tokens = len(message.split())
    n_first_dialog_messages_removed = len(message)
    result = index.query_with_sources(message)
    answer = result["answer"] + "\n SOURCES: " + str(result["sources"])
    response = ResponseModel(
        answer=answer,
        n_input_tokens=n_input_tokens,
        n_output_tokens=len(answer.split()),  # Presumably you are counting tokens in the answer string
        n_first_dialog_messages_removed=n_first_dialog_messages_removed,
        error=False
    )
    return response

@app.get("/test")
async def test_api():
    return {"message": "API works!"}


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8008, log_level="info")
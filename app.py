import click
from genes.config import *

base = Path(".")
locations = Locations(base)

#def run_server():
#    from dash import Dash, dcc, html
#    from dash.dependencies import Input, Output, State, MATCH

    #from components import *

    #app = dash.Dash(__name__, suppress_callback_exceptions=True)
    #app.run_server(debug=True, host="0.0.0.0", port=8050)

#    raise Exception("not yet read!")

#if __name__ == '__main__':
#    run_server()

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import asyncio

app = FastAPI()

# Define a Pydantic model for the request body
class Item(BaseModel):
    username: str
    text: str

# Mock external async function
async def external_function(username: str, text: str):
    # simulate delay
    await asyncio.sleep(1)

    # return json
    return {
        "username": username,
        "text": text
    }

@app.post("/items/")
async def create_item(item: Item):
    result = await external_function(item.username, item.text)
    return result

def index_txt(folder: Path):
    traverse(folder)
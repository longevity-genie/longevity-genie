from pathlib import Path
from pathlib import Path
from textwrap import dedent
from typing import List, Tuple, Union

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import openai
from dash import html
from dash.dependencies import Input, Output, State
from genie.chats import ChatIndex

base = Path(".").absolute().resolve()

def Header(name: str, app: dash.Dash) -> dbc.Row:
    title = html.H1(name, style={"margin-top": 5})
    logo = html.Img(
        src=app.get_asset_url("dash-logo.png"), style={"float": "right", "height": 60}
    )
    return dbc.Row([dbc.Col(title, md=8), dbc.Col(logo, md=4)])


def textbox(text: str, box: str="AI", name: str="Longevity Genie") -> Union[dbc.Card, html.Div]:
    text = text.replace(f"{name}:", "").replace("You:", "")
    style = {
        "max-width": "60%",
        "width": "max-content",
        "padding": "5px 10px",
        "border-radius": 25,
        "margin-bottom": 20,
    }

    if box == "user":
        style["margin-left"] = "auto"
        style["margin-right"] = 0

        return dbc.Card(text, style=style, body=True, color="primary", inverse=True)

    elif box == "AI":
        style["margin-left"] = 0
        style["margin-right"] = "auto"

        thumbnail = html.Img(
            src=app.get_asset_url("Longevity Genie.jpg"),
            style={
                "border-radius": 50,
                "height": 36,
                "margin-right": 5,
                "float": "left",
            },
        )
        textbox = dbc.Card(text, style=style, body=True, color="light", inverse=False)

        return html.Div([thumbnail, textbox])

    else:
        raise ValueError("Incorrect option for `box`.")


# Define app
app: dash.Dash = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# define chat client
chat_index = ChatIndex()

# Load images
IMAGES: dict = {"Longevity Genie": app.get_asset_url("Longevity Genie.jpg")}

# Define Layout
conversation = html.Div(
    html.Div(id="display-conversation"),
    style={
        "overflow-y": "auto",
        "display": "flex",
        "height": "calc(90vh - 132px)",
        "flex-direction": "column-reverse",
    },
)

controls: dbc.InputGroup = dbc.InputGroup(
    children=[
        dbc.Input(id="user-input", placeholder="Write to the chatbot...", type="text"),
        dbc.Button("Submit", id="submit")
    ]
)

app.layout = dbc.Container(
    fluid=False,
    children=[
        Header("Dash GPT-3 Chatbot", app),
        html.Hr(),
        dcc.Store(id="store-conversation", data=""),
        conversation,
        controls,
        dbc.Spinner(html.Div(id="loading-component")),
    ],
)

@app.callback(
    Output("display-conversation", "children"), [Input("store-conversation", "data")]
)
def update_display(chat_history: list[str]) -> List[Union[dbc.Card, html.Div]]:
    return [
        textbox(x, box="user") if i % 2 == 0 else textbox(x, box="AI")
        for i, x in enumerate(chat_history[:-1])
    ]

@app.callback(
    Output("user-input", "value"),
    [Input("submit", "n_clicks"), Input("user-input", "n_submit")],
)
def clear_input(n_clicks: int, n_submit: int) -> str:
    return ""

@app.callback(
    [Output("store-conversation", "data"), Output("loading-component", "children")],
    [Input("submit", "n_clicks"), Input("user-input", "n_submit")],
    [State("user-input", "value"), State("store-conversation", "data")],
)
def run_chatbot(n_clicks: int, n_submit: int, user_input: str, chat_history: str) -> Tuple[str, None]:
    if n_clicks == 0 and n_submit is None:
        return "", None
    
    if user_input is None or user_input == "":
        return chat_history, None

    """
    response = openai.Completion.create(
        engine="davinci",
        prompt=model_input,
        max_tokens=250,
        stop=["You:"],
        temperature=0.9,
    )
    """
    answer = chat_index.answer(user_input)
    updated_history = chat_index.messages
    print(f"UPDATED HISTORY: {updated_history}")
    
    return updated_history, None


if __name__ == '__main__':
    app.run_server(debug=False)
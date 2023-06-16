from pathlib import Path
from typing import List, Tuple, Union

import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State

from genie.chats import ChatIndex, GenieChain, ChainType
from genie.config import Locations

base = Path(".").absolute().resolve()
locations = Locations(base)


#chain_options = ["stuff", "map_reduce", "refine", "map_rerank"]
chain_options = [chain.value for chain in ChainType]
chain_dic = {chain.value: chain for chain in ChainType}

chain_selection = dcc.Dropdown(
    id='chain_type',
    options=[{'label': i, 'value': i} for i in chain_options],
    value='stuff',
    style={'min-width': '150px'}
)

search_options = ["similarity", "mmr"]

search_selection = dcc.Dropdown(
    id='search_type',
    options=[{'label': i, 'value': i} for i in search_options],
    value='similarity',
    style={'min-width': '150px'}
)

genie_chain_options = [chain.value for chain in GenieChain]
genie_chain_dic = {chain.value: chain for chain in GenieChain}

genie_selection = dcc.Dropdown(
    id='genie_chain',
    options=[{'label': i, 'value': i} for i in genie_chain_options],
    value=GenieChain.IndexSource.value,
    style={'min-width': '150px'}
)

def Header(name: str, app: dash.Dash) -> dbc.Row:
    title = html.H1(name, style={"margin-top": 5})
    logo = html.Img(
        src=app.get_asset_url("longevity_genie.jpg"), style={"float": "right", "height": 60}
    )
    return dbc.Row([dbc.Col(title, md=8), dbc.Col(logo, md=4)])


def textbox(text: str, box: str="AI", name: str="Longevity Genie") -> Union[dbc.Card, html.Div]:
    text = text.replace(f"{name}:", "").replace("You:", "")
    style = {
        "max-width": "60%",
        "min-width": "200px",
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
            src=app.get_asset_url("longevity_genie.jpg"),
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
chat_index = ChatIndex(locations.index)

# Load images
IMAGES: dict = {"Longevity Genie": app.get_asset_url("assets/longevity_genie.jpg")}

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
        chain_selection, search_selection, genie_selection,
        dbc.Button("Submit", id="submit")
    ]
)

app.layout = dbc.Container(
    fluid=False,
    children=[
        Header("Longevity Genie chatbot", app),
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
        for i, x in enumerate(chat_history)
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
    [State('genie_chain', 'value')],
    [State('chain_type', 'value')],
    [State('search_type', 'value')]
)
def run_chatbot(n_clicks: int, n_submit: int, user_input: str, chat_history: str, genie_chain: str, chain_type: str, search_type: str) -> Tuple[str, None]:
    if n_clicks == 0 and n_submit is None:
        return "", None
    
    if user_input is None or user_input == "":
        return chat_history, None

    genie_chain_enum = genie_chain_dic[genie_chain]
    chain_type_enum = chain_dic[chain_type]

    if chat_index.chain_type != chain_type or chat_index.search_type != search_type or genie_chain != chat_index.genie_chain.value:
        chat_index.with_updated_chain(genie_chain_enum, chain_type=chain_type_enum, search_type=search_type)
    answer = chat_index.answer(user_input)
    updated_history = chat_index.messages
    print(f"UPDATED HISTORY: {updated_history}")
    return updated_history, None


if __name__ == '__main__':
    app.run_server(debug=False)
    from langchain.server import main
    #from langchain.cli.main import get_docker_compose_command
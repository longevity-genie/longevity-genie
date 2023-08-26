import pprint
from pathlib import Path
from typing import List, Tuple, Union

import dash
import dash_bootstrap_components as dbc
import loguru
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State

from genie.chats import Genie
from genie.config import Locations, fix_memory

# from genie.chats import ChatIndex, GenieChain, ChainType

base = Path(".").absolute().resolve()
locations = Locations(base)

fix_memory()
genie = Genie()


##############################



collection_selection = dcc.Dropdown(
    id='collections',
    options=[{'label': i, 'value': i} for i in genie.collections],
    value='bge_large_512_aging_papers_paragraphs',
    style={'min-width': '250px'}
)

search_options = ["similarity", "mmr"]

search_selection = dcc.Dropdown(
    id='search_type',
    options=[{'label': i, 'value': i} for i in search_options],
    value='similarity',
    style={'min-width': '150px'}
)



"""
genie_chain_options = [chain.value for chain in GenieChain]
genie_chain_dic = {chain.value: chain for chain in GenieChain}

genie_selection = dcc.Dropdown(
    id='genie_chain',
    options=[{'label': i, 'value': i} for i in genie_chain_options],
    value=GenieChain.IndexSource.value,
    style={'min-width': '150px'}
)
"""

def Header(name: str, app: dash.Dash) -> dbc.Row:
    title = html.H1(name, style={"margin-top": 5, "color": "#6200EA"})
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
#chat_index = ChatIndex(locations.index)

# Load images
IMAGES: dict = {"Longevity Genie": app.get_asset_url("assets/longevity_genie.jpg")}

# Define Layout
conversation = html.Div(
    html.Div(id="display-conversation", style={"height": "96vh", "overflow-y": "auto"}),
    style={
        "overflow-y": "auto",
        "display": "flex",
        "height": "calc(96vh - 200px)",
        "flex-direction": "column-reverse",
    },
)

controls: dbc.InputGroup = dbc.InputGroup(
    children=[
        dbc.Input(id="user-input", placeholder="Write to the chatbot...", type="text"),
        collection_selection, search_selection, #genie_selection,
        dbc.Button("Submit", id="submit")
    ]
)

app.layout = dbc.Container([

    Header("Longevity Genie chatbot", app),
    html.Hr(),
    dcc.Store(id="store-conversation", data=[]),
    dbc.Row([
        # Chat Area
        dbc.Col([
            # Chat History
            dbc.Card([
                dbc.CardBody([
                    conversation
                ])
            ], style={'height': 'calc(96vh - 200px)', 'overflowY': 'scroll', 'marginBottom': '10px'}),

            # Message Input and Send Button
            controls
        ], width=8),

        # Right Sidebar
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Right Sidebar"),
                dbc.CardBody([
                    html.P("This is the right sidebar content"),
                    # ... continue with more sidebar content
                ])
            ])
        ], width=4)
    ]), dbc.Spinner(html.Div(id="loading-component"))
])

@app.callback(
    Output("display-conversation", "children"),
    Input("store-conversation", "data")
)
def update_display(data: list[dict]) -> List[Union[dbc.Card, html.Div]]:
    loguru.logger.error(data)
    return [textbox(d["content"], box="AI" if d["type"] == "ai" else "user") for d in data]


@app.callback(
    Output("user-input", "value"),
    [Input("submit", "n_clicks"), Input("user-input", "n_submit")],
)
def clear_input(n_clicks: int, n_submit: int) -> str:
    return ""

@app.callback(
    Output("store-conversation", "data"),
    Output("loading-component", "children"),
    Input("submit", "n_clicks"),
    Input("user-input", "n_submit"),
    State("user-input", "value"),
    State('collections', 'value'),
    State('search_type', 'value')
)
def run_chatbot(n_clicks: int, n_submit: int, user_input: str, collections: str, search_type: str) -> Tuple[list[dict], None]:
    if n_clicks == 0 and n_submit is None:
        return [], None

    if user_input is None or user_input == "":
        return genie.history, None

    answer = genie.message(user_input)
    loguru.logger.error("ANSWER IS: ")
    pprint.pprint(answer)
    return genie.history, None


if __name__ == '__main__':
    app.run_server(debug=False)
    #from langchain.cli.main import get_docker_compose_command
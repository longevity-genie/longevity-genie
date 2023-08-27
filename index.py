import pprint
from pathlib import Path
from typing import List, Tuple, Union

import dash
import dash_bootstrap_components as dbc
import loguru
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from genie.chat import GenieChat
from genie.config import Locations
from genie.enums import SearchType
from genie.retriever import GenieRetriever
from genie.wishes.answers import WishAnswer

# from genie.chats import ChatIndex, GenieChain, ChainType

base = Path(".").absolute().resolve()
locations = Locations(base)


genieRetriever = GenieRetriever.from_collections(
    ["bge_large_512_aging_papers_paragraphs",
     "biolinkbert_large_512_aging_papers_paragraphs"]
)
genie = GenieChat(retriever=genieRetriever, verbose=True)


##############################
search_options = [s.value for s in SearchType]

search_selection = dcc.Dropdown(
    id='search_type',
    options=[{'label': i, 'value': i} for i in search_options],
    value='similarity',
    style={'min-width': '150px'}
)


k_selection = dcc.Dropdown(
    id='k_value',
    options=[{'label': str(i), 'value': i} for i in range(8, 15, 1)],
    value=8,
    style={'min-width': '50px'}
)


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

document_sources = html.Div(
    id="document-sources", style={"overflow-y": "auto"}
)

settings:  dbc.Card = dbc.Card([
    dbc.CardHeader("Search settings"),
    dbc.CardBody([
        dbc.InputGroup([
        search_selection, k_selection])
    ])
])

controls: dbc.InputGroup = dbc.InputGroup(
    children=[
        dbc.Input(id="user-input", placeholder="Write to the chatbot...", type="text"),
        dbc.Button("Submit", id="submit")
    ]
)

app.layout = dbc.Container([

    Header("Longevity Genie Chat", app),
    html.Hr(),
    dcc.Store(id="store-conversation", data=[]),
    dcc.Store(id="store-documents", data=[]),
    dbc.Row([
        # Chat Area
        dbc.Col([
            # Chat History
            dbc.Card([
                dbc.CardBody([
                    conversation
                ])
            ], style={'height': 'calc(94vh - 300px)', 'overflowY': 'scroll', 'marginBottom': '10px'}),
            settings, controls
        ], width=8),

        # Right Sidebar
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Retrieved documents"),
                dbc.CardBody([
                    document_sources
                ])
            ])
        ], width=4)
    ]), dbc.Spinner(html.Div(id="loading-component"))
], style={"maxWidth": "95%"})

@app.callback(
    Output("display-conversation", "children"),
    Input("store-conversation", "data")
)
def render_chat(data: list[dict]) -> List[Union[dbc.Card, html.Div]]:
    return [textbox(d["content"], box="AI" if d["type"] == "ai" else "user") for d in data]


def render_accordion_for_documents(document_data: list[dict]) -> dbc.Accordion:
    """
    This function creates an accordion component for the provided document data using the Accordion component.
    """
    accordion_items = []
    for index, doc in enumerate(document_data):
        # Build the form content for each document
        form_content = []

        # Determine the title based on the type and content of annotations_title
        if isinstance(doc['annotations_title'], list):
            title = doc['annotations_title'][0] if doc['annotations_title'] else "No title found"
        elif doc['annotations_title'] is None:
            title = "No title found"
        else:
            title = doc['annotations_title']

        # Add each field (except for page_content) as a separate form field with label using Row and Col
        for field, value in doc.items():
            if field != "page_content" and value is not None:  # Exclude None values from display
                form_content.append(
                    dbc.Row([
                        dbc.Col(dbc.Label(field.capitalize(), className="mr-2"), width=4),
                        dbc.Col(dbc.Input(type="text", value=value, readonly=True))
                    ])
                )

        # Add page_content as a textarea
        form_content.append(dbc.Label("Page Content", className="mr-2"))
        form_content.append(dbc.Textarea(value=doc.get("page_content", ""), style={"min-height": "300px"}, readonly=True))

        # Create the accordion item using AccordionItem component
        accordion_item = dbc.AccordionItem(
            title=title,
            children=form_content,

            item_id=str(index)
        )
        accordion_items.append(accordion_item)

    # Create the accordion using the Accordion component
    accordion = dbc.Accordion(accordion_items)

    return accordion



@app.callback(
    Output("document-sources", "children"),
    Input("store-documents", "data")
)
def render_documents(data: list[dict]) -> List[Union[dbc.Card, html.Div]]:
    return render_accordion_for_documents(data)

@app.callback(
    Output("user-input", "value"),
    [Input("submit", "n_clicks"), Input("user-input", "n_submit")],
)
def clear_input(n_clicks: int, n_submit: int) -> str:
    return ""

@app.callback(
    Output("store-conversation", "data"),
    Output("store-documents", "data"),
    Output("loading-component", "children"),
    Input("submit", "n_clicks"),
    Input("user-input", "n_submit"),
    State("user-input", "value"),
    State('search_type', 'value'),
    State('k_value', 'value'))
def run_chatbot(n_clicks: int, n_submit: int, user_input: str, search_type: str, k_value: int) -> Tuple[list[dict], list[dict], None]:
    if n_clicks == 0 and n_submit is None:
        return [],[], None

    if user_input is None or user_input == "":
        return genie.history, [], None

    genie.retriever = genieRetriever.with_updated_retrievers(k = k_value, search_type=SearchType[search_type])
    answer = genie.message(user_input)
    wish_answer = WishAnswer.from_dict(answer)
    return genie.history, wish_answer.json_sources(), None


if __name__ == '__main__':
    app.run_server(debug=False)
    #from langchain.cli.main import get_docker_compose_command
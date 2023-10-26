import pprint
from pathlib import Path
from typing import List, Tuple, Union

import dash
import dash_bootstrap_components as dbc
import loguru
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from langchain.chat_models import ChatOpenAI
from longdata.longevity_data_chain import LongevityDataChain

from genie.chat import GenieChat
from genie.enums import SearchType
from genie.retriever import GenieRetriever
from genie.wishes.answers import WishAnswer

#HERE WE DEFINE THE DEFAULT CONFI
compression = False
k = 4
model_name = "gpt-3.5-turbo-16k" #gpt-4
llm = ChatOpenAI(model=model_name, temperature=0)

#initializing agents
agent = LongevityDataChain.from_folder(llm, Path("data"), return_intermediate_steps=True)
agents = [agent] #let's comment it out for open-debugging #[agent]

#initializaing retriever
genieRetriever = GenieRetriever.from_collections(agents=agents, k=k)
genie = GenieChat(retriever=genieRetriever, verbose=True, compression=compression)


##############################
search_options = [s.value for s in SearchType]

html.Label('Select Search Type:', style={'margin-right': '10px'}),


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


collections_dropdown = dcc.Dropdown(
    id='collections_selector',
    options=[{'label': i, 'value': i} for i in genieRetriever.all_collections],
    multi=True,
    value=genieRetriever.all_collections,
    style={'min-width': '300px'}
)

search_selection = dcc.Dropdown(
    id='search_type',
    options=[{'label': i, 'value': i} for i in search_options],
    value='similarity',
    style={'min-width': '150px'}
)

model_selection = dcc.Dropdown(
    id='model',
    options=["gpt-4", "gpt-3.5-turbo-16k"],
    value='gpt-3.5-turbo-16k',
    style={'min-width': '150px'}
)

k_selection = dcc.Dropdown(
    id='k_value',
    options=[{'label': str(i), 'value': i} for i in range(3, 10, 1)],
    value=k,
    style={'min-width': '50px'}
)

compressor_checkbox = dcc.Checklist(
    id='compressor_checkbox',
    options=[{'label': 'Use Compressor', 'value': 'use_compressor'}],
    value=['use_compressor'],
    inline=compression
)


settings = html.Div(id="settings", children = [

    # First row: Search Type Selector, K Value Selector, and Compressor Checkbox
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Col(html.Label('Select Search Type:', style={'margin-right': '10px'}), width="auto"),
                dbc.Col(search_selection, style={'padding-left': '0px'})
            ])
        ], width=4, style={'margin-bottom': '10px'}),

        dbc.Col([
            dbc.Row([
                dbc.Col(html.Label('Select K Value:', style={'margin-right': '10px'}), width="auto"),
                dbc.Col(k_selection, style={'padding-left': '0px'})
            ])
        ], width=4, style={'margin-bottom': '10px'}),

        dbc.Col([
            dbc.Row([
                dbc.Col(compressor_checkbox, width="auto")
            ])
        ], width=4, style={'margin-bottom': '10px', 'padding-left': '0px'})
    ]),

    # Second row: Collections Selector
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Col(html.Label('Model selection:', style={'margin-right': '10px'}), width="auto"),
                dbc.Col(model_selection, style={'padding-left': '0px'})
            ])
        ], width=4),
        dbc.Col([
            dbc.Row([
                dbc.Col(html.Label('Select Collections:', style={'margin-right': '10px'}), width="auto"),
                dbc.Col(collections_dropdown, style={'padding-left': '0px'})
            ])
        ], width=8)
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
            ], style={'height': 'calc(94vh - 320px)', 'overflowY': 'scroll', 'marginBottom': '10px'}),
            settings,html.Hr(), controls
        ], width=7),



        # Right Sidebar
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Retrieved documents"),
                dbc.CardBody([
                    document_sources
                ])
            ])
        ], width=5)
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
            title=doc["title"],
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
    State("collections_selector", "value"),
    State("compressor_checkbox", "value"),
    State("model", "value"),
    State("user-input", "value"),
    State('search_type', 'value'),
    State('k_value', 'value'))

def run_chatbot(n_clicks: int, n_submit: int, collections_selected: List[str], compressor_checkbox: list,  model: str, user_input: str, search_type: str, k_value: int) -> Tuple[list[dict], list[dict], None]:
    if n_clicks == 0 and n_submit is None:
        return [],[], None

    if user_input is None or user_input == "":
        return genie.history, [], None
    if genie.llm.model_name != model:
        loguru.logger.info(f"changing model to {model}")
        genie.llm.model_name = model
    genie._retriever = genieRetriever.with_updated_retrievers(k = k_value,
                                                             search_type=SearchType[search_type],
                                                             collection_names=collections_selected)
    to_compress = compressor_checkbox is not None and len(compressor_checkbox) > 0
    genie.compress(to_compress)
    answer = genie.message(user_input)
    wish_answer = WishAnswer.from_dict(answer)
    return genie.history, wish_answer.json_sources(), None


if __name__ == '__main__':
    app.run_server(host= '0.0.0.0', debug=True)
    #from langchain.cli.main import get_docker_compose_command
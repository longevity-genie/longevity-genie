import click
from genes.config import *

base = Path(".")
locations = Locations(base)

def run_server():
    from dash import Dash, dcc, html
    from dash.dependencies import Input, Output, State, MATCH

    #from components import *

    #app = dash.Dash(__name__, suppress_callback_exceptions=True)
    #app.run_server(debug=True, host="0.0.0.0", port=8050)

    raise Exception("not yet read!")

if __name__ == '__main__':
    run_server()
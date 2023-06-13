import os
from pathlib import Path

import click
import polars as pl
from click.core import Context
from langchain.agents import AgentExecutor

from genie.agents import init_csv_agent, init_simple_llm_agent
from genie.constants import prompt_5
from genie.config import Locations, load_openai_key, start_tracing
from genie.indexing import Index
from langchainplus_sdk import LangChainPlusClient


@click.group(invoke_without_command=True)
@click.pass_context
def app(ctx: Context):
    if ctx.invoked_subcommand is None:
        click.echo('Running the default command...')


def write_database_dataset():
    from langchainplus_sdk import LangChainPlusClient
    client = LangChainPlusClient()
    client.create_dataset()
    #TODO finish




if __name__ == '__main__':
    start_tracing()
    openai_key = load_openai_key(debug=True)
    print(f"The key is {openai_key}")
    app()
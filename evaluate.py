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

@click.group(invoke_without_command=True)
@click.pass_context
def app(ctx: Context):
    if ctx.invoked_subcommand is None:
        click.echo('Running the default command...')
        test()

def test():
    import os
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_ENDPOINT"] = "https://api.langchain.plus"
    os.environ["LANGCHAIN_API_KEY"] = "32a6068697d449999226472a626e3e06"
    # All LangChain code will be traced to the default session
    from langchain import OpenAI
    hello = OpenAI().predict("Hello, world!")
    print(f"Hello message {hello}")

if __name__ == '__main__':
    start_tracing()
    openai_key = load_openai_key(debug=True)
    print(f"The key is {openai_key}")
    app()
from pathlib import Path

import click
from typing import Optional
from langchain.chat_models import ChatOpenAI
from longdata.longevity_data_chain import LongevityDataChain

from genie.retriever import GenieRetriever
from genie.chat import GenieChat

import click
from typing import Optional, List

@click.command()
@click.option('--message', prompt='Enter a message', required=True, help='The message string.')
@click.option('--model', default="gpt-3.5-turbo-16k", help='The model name string.')
@click.option('--agents_model', default="gpt-4", help='The model name string.')
@click.option('--k', default=4, type=click.INT, help='Number of results to return per retriever')
@click.option('--compression', default=True, type=click.BOOL, help='Boolean flag for compression.')
@click.option('--collections', default=["bge_large_512_aging_papers_paragraphs", "biolinkbert_large_512_aging_papers_paragraphs"], multiple=True, help='Array of collection names.')
@click.option('--history', default=False, type=click.BOOL, help='Boolean flag for printing history')
def ask(message: str, model: str, agents_model: str, k: int, compression: bool, collections: Optional[List[str]], history: bool):
    """
    A simple Click console application.
    """
    click.echo(f"Message: {message}")
    click.echo(f"Model Name: {model}")
    if collections:
        click.echo(f"Collections: {', '.join(collections)}")
    else:
        click.echo("No collections provided.")

    agent_llm = ChatOpenAI(model=agents_model, temperature=0)
    agent = LongevityDataChain.from_folder(agent_llm, Path("data"), return_intermediate_steps=True)
    genieRetriever = GenieRetriever.from_collections(collection_names=collections, k=k, agents=[agent])
    genie = GenieChat(retriever=genieRetriever, verbose=True, compression=compression)
    answer = genie.message(message)
    click.echo(f"MODEL ANSWER IS {answer}")
    if history:
        click.echo(f"CHAT HISTORY IS {genie.history}")

if __name__ == '__main__':
    ask()

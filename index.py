import click

from genes.downloads import download_papers
from genes.indexing import *
from genes.prepare import with_papers_incremental
from genes.config import Locations
from pathlib import Path
from dotenv import load_dotenv
from genes.indexing import *

@click.group(invoke_without_command=True)
@click.pass_context
def app(ctx):
    if ctx.invoked_subcommand is None:
        click.echo('Running the default command...')
        test_index()

@app.command("write")
@click.option('--model', default='gpt-4', help='model to use, gpt-4 by default')
@click.option('--base', default='.', help='base folder')
def write(model: str, base: str):
    load_dotenv()
    locations = Locations(Path(base))
    index = Index(locations, model)
    print("saving modules and papers")
    index.with_modules().with_papers().persist()


@app.command("test")
@click.option('--base', default='.', help='base folder')
def test_index(base: str):
    load_dotenv()
    locations = Locations(Path(base))
    index = Index(locations, "gpt-4") #Index(locations, "gpt-4")
    question1 = f"what is association of GSTT1 genetic variant with longevity?"
    print(f"Q1: {question1}")
    answer1 = index.query_with_sources(question1)
    print(f"A1: {answer1}")
    question2 = f'The genome has the following genetic variants: rs1801133, rs1799752, rs1799889, rs1800790, rs1799752, what are their associations with longevity?'
    print(f"Q2: {question2}")
    answer2 = index.query_with_sources(question2)
    print(f"A2: {answer2}")

if __name__ == '__main__':
    app()
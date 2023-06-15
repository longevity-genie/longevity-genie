import click
import openai
from click import Context
from langchain.embeddings import VertexAIEmbeddings, LlamaCppEmbeddings
from genie.prepare.papers import papers_to_documents
from genie.config import load_environment_keys, Locations
from genie.prepare.papers import with_papers_incremental
from genie.prepare.index import *
from genie.prepare.downloads import *
from pathlib import Path

@click.group(invoke_without_command=False)
@click.pass_context
def app(ctx: Context):
    #if ctx.invoked_subcommand is None:
    #    click.echo('Running the default command...')
    #    test_index()
    pass

@app.command("papers_index")
@click.option('--collection', default='papers', help='papers collection name')
@click.option('--chunk_size', type=click.INT, default=6000, help='size of the chunk for splitting')
@click.option('--embeddings', type=click.Choice(["openai", "lambda", "vertexai"]), default="openai", help='size of the chunk for splitting')
@click.option('--base', default='.', help='base folder')
def papers_index(collection: str, chunk_size: int, embeddings: str,  base: str):
    locations = Locations(Path(base))
    openai_key = load_environment_keys()
    embeddings_function: Optional[Embeddings]
    if embeddings == "openai":
        embeddings_function = OpenAIEmbeddings()
    elif embeddings == "lambda":
        embeddings_function = LlamaCppEmbeddings()
    elif embeddings == "vertexai":
        embeddings_function = VertexAIEmbeddings()
    else:
        print(f"{embeddings} is not yet supported by CLI, using default openai embeddings instead")
        embeddings_function = OpenAIEmbeddings()
    print(f"embeddings are {embeddings}")
    where = locations.paper_index / f"{embeddings}_{chunk_size}_chunk"
    where.mkdir(exist_ok=True, parents=True)
    print(f"writing index of papers to {where}")
    documents = papers_to_documents(locations.papers)
    return write_db(where, collection, documents, chunk_size, embeddings = embeddings_function)


@app.command("download_papers")
@click.option('--module', default='just_longevitymap', help='module to download data from')
@click.option('--table', default='variant', help='sqlite table')
@click.option('--pubmed', default='quickpubmed', help='field that contains pubmed papers')
@click.option('--base', default='.', help='base folder')
def download_papers_command(module: str, table: str, pubmed: str, base: str):
    return download_papers(module, table, pubmed, base)
    #/data/users/antonkulaga/.oakvar/modules


@app.command("parse_papers")
@click.option('--base', default='.', help='base folder')
def parse(base: str):
    locations = Locations(Path(base))
    return with_papers_incremental(locations.papers)


if __name__ == '__main__':
    app()
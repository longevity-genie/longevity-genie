import click
from pathlib import Path

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

from genes.config import Locations
from genes.sqlite import *
from genes.downloads import *

import sys
from pathlib import Path
from genes.config import Locations
from pycomfort.files import *

@click.group(invoke_without_command=True)
@click.pass_context
def app(ctx):
    if ctx.invoked_subcommand is None:
        click.echo('Running the default command...')
        download_papers()

@app.command()
@click.option('--base', default='.', help='base folder')
def index(base: str):
    from langchain.document_loaders import UnstructuredPDFLoader
    from langchain.indexes import VectorstoreIndexCreator
    locations = Locations(Path(base))
    from langchain.document_loaders import DataFrameLoader
    modules_loaders = [DataFrameLoader(pd.read_csv(tsv, sep="\t"), page_content_column="identifier") for tsv in with_ext(locations.modules_data, "tsv")]
    papers = traverse(locations.papers, lambda p: "pdf" in p.suffix)
    #pdf_loaders = [UnstructuredPDFLoader(str(p)) for p in papers]
    pdf_loaders = [UnstructuredPDFLoader(str(p)) for p in papers[0:2]]
    loaders = modules_loaders + pdf_loaders
    #loaders = []
    print("let's try to index")
    index = VectorstoreIndexCreator(vectorstore_kwargs={"persist_directory": str(locations.paper_index)}).from_loaders(loaders)
    print(f"indexing kind of finished, it will be saved to {locations.paper_index}")
    #apoe_result = index.query_with_sources("What do you know about APOE gene?")
    test_result = "MTHFR"
    print(index.query_with_sources(f"What is {test_result}?"))

@app.command()
@click.option('--module', default='just_longevitymap', help='module to download data from')
@click.option('--table', default='variant', help='sqlite table')
@click.option('--pubmed', default='quickpubmed', help='field that contains pubmed papers')
@click.option('--base', default='.', help='base folder')
def download_papers(module: str, table: str, pubmed: str, base: str):
    base_path: Path = Path(base)
    locations = Locations(base_path)
    module_folder = locations.modules / module
    click.echo(f"preparing the dataframe for {table} with pubmed {pubmed} field for module f{module} at f{module_folder}")
    df = prepare_dataframe(locations, module, module_folder, pubmed, table)
    dois = set(df["source"].to_list())
    return [try_download(doi, locations.papers, True) for doi in dois]



def prepare_dataframe(locations: Locations, module: str, module_folder: Path, pubmed: str, table: str):
    module_data = module_folder / "data"
    assert module_folder.exists() and module_data, f"{module_data} should exist!"
    db = with_ext(module_data, "sqlite").to_list()[0]
    print(f"getting info from {table}")
    df = get_table_df(db, table).drop(columns=['id']).dropna()
    click.echo(f"transforming pubmed ids to doi")
    df['source'] = df[pubmed].apply(lambda p: try_doi_from_pubmed(p).get_or_else_get(lambda v: p))
    csv_path = locations.modules_data / f"{module}.tsv"
    click.echo(f"saving results to {csv_path}")
    click.echo(f"writing dataframe to {csv_path}")
    df.to_csv(csv_path, sep="\t")
    return df


if __name__ == '__main__':
    app()
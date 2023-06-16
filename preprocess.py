from pathlib import Path

import click
from click import Context

from genie.config import load_environment_keys
from genie.prepare.downloads import *
from genie.prepare.index import *
from genie.prepare.papers import papers_to_documents
from genie.prepare.papers import with_papers_incremental
from genie.prepare.modules import prepare_longevity, prepare_coronary, prepare_clinvar


@click.group(invoke_without_command=False)
@click.pass_context
def app(ctx: Context):
    #if ctx.invoked_subcommand is None:
    #    click.echo('Running the default command...')
    #    test_index()
    pass

@app.command("modules_text")
def prepare_modules_text():
    from genie.prepare.modules import prepare_longevity
    print("preparing longevity map")
    locations: Locations
    prepare_longevity()

@app.command("prepare_longevity_text")
@click.option('--module', type=click.Path(exists=True), default=None, help="path to LongevityMap module")
@click.option('--base', default='.', help='base folder')
def prepare_longevity_text(module: Optional[str], base: str):
    locations = Locations(Path(base))
    just_longevity_map = locations.just_longevitymap if module is None else Path(module)
    longevity_map_text = prepare_longevity(just_longevity_map, locations.dois)
    where = locations.longevity_map_text
    longevity_map_text.write_csv(str(where), sep="\t")
    print(f"written to {where}")
    return where


@app.command("prepare_coronary_text")
@click.option('--module', type=click.Path(exists=True), default=None, help="path to Coronary module")
@click.option('--base', default='.', help='base folder')
def prepare_coronary_text(module: Optional[str], base: str):
    locations = Locations(Path(base))
    just_coronary = locations.just_coronary if module is None else Path(module)
    coronary_text = prepare_coronary(just_coronary)
    where = locations.coronary_text
    coronary_text.write_csv(str(where), sep="\t")
    print(f"written to {where}")
    return where

@app.command("prepare_clinvar_text")
@click.option('--module', type=click.Path(exists=True), default=None, help="path to ClinVar module")
@click.option('--base', default='.', help='base folder')
def prepare_clinvar_text(module: Optional[str], base: str):
    locations = Locations(Path(base))
    just_clinvar = locations.clinvar if module is None else Path(module)
    clinvar_text = prepare_clinvar(just_clinvar)
    where = locations.clinvar_text
    clinvar_text.write_csv(str(where), sep="\t")
    print(f"written to {where}")
    return where



"""
@app.command("prepare_longevity_text")
@click.option('--chunk_size', type=click.INT, default=6000, help='size of the chunk for splitting')
@click.option('--base', default='.', help='base folder')
def prepare_longevity_text(longevity_module: Optional[str], chunk_size: int, embeddings: str, base: str):
    locations = Locations(Path(base))
    from genie.prepare.modules import prepare_longevity
    embeddings_function = genie.config.resolve_embeddings(embeddings)
    just_longevity_map = locations.just_longevitymap if longevity_module is None else Path(longevity_module)
    return prepare_longevity(just_longevity_map, locations.dois, locations.longevity_map_text)
"""

"""
@app.command("modules_index")
@click.option('--module', type=click.Choice(["longevity_map", "coronary", ""]), default="longevity_map", help='papers collection name')
@click.option('--chunk_size', type=click.INT, default=6000, help='size of the chunk for splitting')
@click.option('--embeddings', type=click.Choice(["openai", "lambda", "vertexai"]), default="openai", help='size of the chunk for splitting')
@click.option('--base', default='.', help='base folder')
def modules_index(module: str, chunk_size: int, embeddings: str,  base: str):
    from genie.prepare.modules import prepare_clinvar, prepare_longevity, prepare_coronary
    if module == "longevity_map":
"""


@app.command("papers_index")
@click.option('--collection', default='papers', help='papers collection name')
@click.option('--chunk_size', type=click.INT, default=6000, help='size of the chunk for splitting')
@click.option('--embeddings', type=click.Choice(["openai", "lambda", "vertexai"]), default="openai", help='size of the chunk for splitting')
@click.option('--base', default='.', help='base folder')
def papers_index(collection: str, chunk_size: int, embeddings: str,  base: str):
    locations = Locations(Path(base))
    openai_key = load_environment_keys()
    embeddings_function = config.resolve_embeddings(embeddings)
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
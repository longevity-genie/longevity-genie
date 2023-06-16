#!/usr/bin/env python3

from pathlib import Path

import click
from click import Context

from genie.config import load_environment_keys
from genie.prepare.downloads import *
from genie.prepare.index import *
from genie.prepare.papers import papers_to_documents
from genie.prepare.papers import with_papers_incremental
from genie.prepare.modules import prepare_longevity, prepare_coronary, prepare_clinvar, tsv_to_documents
from genie.config import resolve_embeddings

@click.group(invoke_without_command=False)
@click.pass_context
def app(ctx: Context):
    #if ctx.invoked_subcommand is None:
    #    click.echo('Running the default command...')
    #    test_index()
    pass


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


@app.command("index_modules")
@click.option('--collection', default='modules', help='modules collection name')
@click.option('--chunk_size', type=click.INT, default=6000, help='size of the chunk for splitting')
@click.option('--embeddings', type=click.Choice(["openai", "lambda", "vertexai"]), default="openai", help='size of the chunk for splitting')
@click.option('--base', default='.', help='base folder')
def index_modules(collection: str, chunk_size: int, embeddings: str,  base: str):
    locations = Locations(Path(base))
    openai_key = load_environment_keys()
    print(f"embeddings are {embeddings}")
    where = locations.index / f"{embeddings}_{chunk_size}_chunk"
    where.mkdir(exist_ok=True, parents=True)
    print(f"writing index of modules to {where}")
    documents = tsv_to_documents(locations.modules_text_data)
    embeddings_function = resolve_embeddings(embeddings)
    return write_db(where, collection, documents, chunk_size, embeddings = embeddings_function)

@app.command("index_papers")
@click.option('--collection', default='papers', help='papers collection name')
@click.option('--chunk_size', type=click.INT, default=6000, help='size of the chunk for splitting')
@click.option('--embeddings', type=click.Choice(["openai", "lambda", "vertexai"]), default="openai", help='size of the chunk for splitting')
@click.option('--base', default='.', help='base folder')
def index_papers(collection: str, chunk_size: int, embeddings: str,  base: str):
    locations = Locations(Path(base))
    openai_key = load_environment_keys()
    embeddings_function = resolve_embeddings(embeddings)
    print(f"embeddings are {embeddings}")
    where = locations.index / f"{embeddings}_{chunk_size}_chunk"
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
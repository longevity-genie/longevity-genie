import click

from genes.downloads import download_papers
from genes.indexing import *
from genes.prepare import with_papers_incremental


@click.group(invoke_without_command=True)
@click.pass_context
def app(ctx):
    if ctx.invoked_subcommand is None:
        click.echo('Running the default command...')
        download_papers()


@app.command()
@click.option('--base', default='.', help='base folder')
def index(base: str):
    locations = Locations(Path(base))
    index = Index(locations)
    index.with_modules(locations.modules_data)
    index.with_papers_incremental()
    index.persist()
    index


@app.command("download_papers")
@click.option('--module', default='just_longevitymap', help='module to download data from')
@click.option('--table', default='variant', help='sqlite table')
@click.option('--pubmed', default='quickpubmed', help='field that contains pubmed papers')
@click.option('--base', default='.', help='base folder')
def download_papers_command(module: str, table: str, pubmed: str, base: str):
    return download_papers(module, table, pubmed, base)
    #/data/users/antonkulaga/.oakvar/modules


@app.command("parse")
@click.option('--base', default='.', help='base folder')
def parse(base: str):
    locations = Locations(Path(base))
    return with_papers_incremental(locations.papers)


if __name__ == '__main__':
    app()
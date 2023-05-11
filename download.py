from genes.indexing import *

from genes.config import Locations
from pycomfort.files import *
from pycomfort.files import *

from genes.config import Locations
from genes.indexing import *


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
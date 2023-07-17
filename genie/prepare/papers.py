from pathlib import Path

from getpaper.download import try_doi_from_pubmed, try_download
from pycomfort.files import with_ext

from genie.config import Locations
from genie.prepare.sqlite import get_table_df


# TODO: maybe outdated, need to rewrite
def prepare_dataframe_for_download(locations: Locations, module: str, module_folder: Path, pubmed: str, table: str):
    module_data = module_folder / "data"
    assert module_folder.exists() and module_data, f"{module_data} should exist!"
    db = with_ext(module_data, "sqlite").to_list()[0]
    print(f"getting info from {table}")
    df = get_table_df(db, table).drop(columns=['id']).dropna()
    print(f"transforming pubmed ids to doi")
    df['source'] = df[pubmed].apply(lambda p: try_doi_from_pubmed(p).get_or_else_get(lambda v: ""))
    csv_path = locations.modules_data / f"{module}.tsv"
    print(f"saving results to {csv_path}")
    print(f"writing dataframe to {csv_path}")
    df.to_csv(csv_path, sep="\t")
    return df

# TODO: will be removed in favour of getpaper implementation

def download_papers(module: str, table: str, pubmed: str, base: str):
    base_path: Path = Path(base)
    locations = Locations(base_path)
    module_folder = locations.modules / module
    print(f"preparing the dataframe for {table} with pubmed {pubmed} field for module f{module} at f{module_folder}")
    df = prepare_dataframe_for_download(locations, module, module_folder, pubmed, table)
    dois = set(df["source"].to_list())
    return [try_download(doi, locations.papers, True) for doi in dois]
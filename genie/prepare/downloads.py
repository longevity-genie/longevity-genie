import xml.etree.ElementTree as ET
from pathlib import Path

import requests
from pycomfort.files import with_ext
from pynction import Try
from scidownl import scihub_download

from genie.sqlite import get_table_df


def doi_from_pubmed(pubmed_id: str):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        "db": "pubmed",
        "id": pubmed_id,
        "retmode": "xml"
    }
    response = requests.get(base_url, params=params)
    #response.raise_for_status()
    root = ET.fromstring(response.content)
    article = root.find(".//PubmedArticle")
    if article is None:
        raise ValueError("PubMed ID not found")
    doi_element = article.find(".//ArticleId[@IdType='doi']")
    if doi_element is None:
        raise ValueError("DOI not found for this PubMed ID")
    return doi_element.text

def try_doi_from_pubmed(pubmed: str) -> Try[str]:
    #print(f"{pubmed} to doi")
    return Try.of(lambda: doi_from_pubmed(pubmed))

def try_download(doi: str, papers: Path, skip_if_exist: bool = True) -> Try[Path]:
    doi_url = f"https://doi.org/{doi}"
    paper = (papers / f"{doi}.pdf").absolute().resolve()
    if skip_if_exist and paper.exists():
        print(f"Paper {paper} for {doi} already exists!")
        return paper
    return Try.of(lambda: scihub_download(doi_url, paper_type="doi", out= paper)).map(lambda _: paper)

def download_pubmed(pubmed: str, papers: Path, skip_if_exist: bool = True):
    try_resolve = try_doi_from_pubmed(pubmed)
    return try_resolve.flat_map(lambda doi: try_download(doi, papers, skip_if_exist))


from genie.config import Locations

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

def download_papers(module: str, table: str, pubmed: str, base: str):
    base_path: Path = Path(base)
    locations = Locations(base_path)
    module_folder = locations.modules / module
    print(f"preparing the dataframe for {table} with pubmed {pubmed} field for module f{module} at f{module_folder}")
    df = prepare_dataframe_for_download(locations, module, module_folder, pubmed, table)
    dois = set(df["source"].to_list())
    return [try_download(doi, locations.papers, True) for doi in dois]

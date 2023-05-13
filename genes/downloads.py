import xml.etree.ElementTree as ET

import requests
from pynction import Try
from scidownl import scihub_download
from pathlib import Path

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
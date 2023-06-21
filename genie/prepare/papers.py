from pathlib import Path
from typing import Optional, List

from langchain.document_loaders import UnstructuredPDFLoader
from langchain.schema import Document
from pycomfort.files import traverse

import xml.etree.ElementTree as ET
from pathlib import Path

import requests
from pycomfort.files import with_ext
from pynction import Try
from scidownl import scihub_download

from genie.sqlite import get_table_df
from getpaper.download import try_doi_from_pubmed, try_download

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

# TODO: will be removed in favour of getpaper implementation

def download_papers(module: str, table: str, pubmed: str, base: str):
    base_path: Path = Path(base)
    locations = Locations(base_path)
    module_folder = locations.modules / module
    print(f"preparing the dataframe for {table} with pubmed {pubmed} field for module f{module} at f{module_folder}")
    df = prepare_dataframe_for_download(locations, module, module_folder, pubmed, table)
    dois = set(df["source"].to_list())
    return [try_download(doi, locations.papers, True) for doi in dois]


def papers_to_documents(folder: Path, proofread: bool = False):
    txt = traverse(folder, lambda p: "txt" in p.suffix)
    texts = [t for t in txt if "_proofread.txt" in t.name] if proofread else txt
    docs: List[Document] = []
    for t in texts:
        doi = f"http://doi.org/{t.parent.name}/{t.stem}"
        with open(t, 'r') as file:
            text = file.read()
            if len(text)<10:
                print("TOO SHORT TEXT")
            else:
                doc = Document(
                    page_content = text,
                    metadata={"source": doi}
                )
                docs.append(doc)
    return docs

def parse_papers(folder: Optional[Path] = None, skip_existing: bool = True):
    papers: list[Path] = traverse(folder, lambda p: "pdf" in p.suffix)
    print(f"indexing {len(papers)} papers")
    i = 1
    max = len(papers)
    for p in papers:
        loader = UnstructuredPDFLoader(str(p))
        print(f"adding paper {i} out of {max}")
        docs: list[Document] = loader.load()
        if len(docs) ==1:
            f = p.parent / f"{p.stem}.txt"
            print(f"writing {f}")
            f.write_text(docs[0].page_content)
        else:
            for i, doc in enumerate(docs):
                f = (p.parent / f"{p.stem}_{i}.txt")
                print(f"writing {f}")
                f.write_text(doc.page_content)
        i = i + 1
    print("papers loading finished")

def with_papers_incremental(folder: Optional[Path] = None, skip_existing: bool = True):
    papers: list[Path] = traverse(folder, lambda p: "pdf" in p.suffix)
    print(f"indexing {len(papers)} papers")
    i = 1
    max = len(papers)
    for p in papers:
        loader = UnstructuredPDFLoader(str(p))
        print(f"adding paper {i} out of {max}")
        docs: list[Document] = loader.load()
        if len(docs) ==1:
            f = p.parent / f"{p.stem}.txt"
            print(f"writing {f}")
            f.write_text(docs[0].page_content)
        else:
            for i, doc in enumerate(docs):
                f = (p.parent / f"{p.stem}_{i}.txt")
                print(f"writing {f}")
                f.write_text(doc.page_content)
        i = i + 1
    print("papers loading finished")
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
from langchain.document_loaders import UnstructuredPDFLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.document_loaders import DataFrameLoader

def make_paper_loaders(locations: Locations):
    print(f"loading papers from {locations.papers}")
    papers = traverse(locations.papers, lambda p: "pdf" in p.suffix)
    pdf_loaders = [UnstructuredPDFLoader(str(p)) for p in papers]
    return pdf_loaders

def index(locations: Locations, load_modules: bool = True, load_papers: bool = True):
    modules_loaders = [DataFrameLoader(pd.read_csv(tsv, sep="\t"), page_content_column="identifier") for tsv in with_ext(locations.modules_data, "tsv")] if load_modules else []
    pdf_loaders = make_paper_loaders(locations) if load_papers else []
    loaders = modules_loaders + pdf_loaders
    index = VectorstoreIndexCreator(vectorstore_kwargs={"persist_directory": str(locations.paper_index)}).from_loaders(loaders)
    print(f"indexing kind of finished, it will be saved to {locations.paper_index}")
    #apoe_result = index.query_with_sources("What do you know about APOE gene?")
    test_result = "MTHFR"
    print(index.query_with_sources(f"What is {test_result}?"))
    return index
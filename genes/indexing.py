from typing import List

import click
from pathlib import Path

from langchain import VectorDBQA, OpenAI
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.embeddings import OpenAIEmbeddings
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter, TextSplitter
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
from unstructured.partition.pdf import partition_pdf

class Index:

    locations: Locations
    persist_directory: Path
    embedding: OpenAIEmbeddings
    db: Chroma
    llm: OpenAI
    chain: RetrievalQAWithSourcesChain
    splitter: TextSplitter

    def __init__(self, locations: Locations):
        self.locations = locations
        self.persist_directory = self.locations.paper_index
        self.embedding = OpenAIEmbeddings()
        self.db = Chroma(persist_directory=str(self.persist_directory),
                         embedding_function=self.embedding
                         )
        self.chain = self.make_chain()


    def make_chain(self):
        self.llm = OpenAI()
        return RetrievalQAWithSourcesChain.from_chain_type(
            self.llm, retriever=self.db.as_retriever()
        )


    def query_with_sources(self, question: str):
        return self.chain({self.chain.question_key: question})

    def papers_to_documents(self, folder: Path):
        papers = traverse(folder, lambda p: "pdf" in p.suffix)
        print(f"indexing {len(papers)} papers")
        return seq([UnstructuredPDFLoader(str(p)).load() for p in papers]).flatten().to_list()

    def modules_to_documents(self, folder: Path):
        modules_loaders = [DataFrameLoader(pd.read_csv(tsv, sep="\t"), page_content_column="identifier") for tsv in with_ext(folder, "tsv")]
        print(f"indexing {len(modules_loaders)} modules")
        modules_docs = seq([loader.load() for loader in modules_loaders]).flatten().to_list()
        return modules_docs

    def with_default_modules(self):
        return self.with_modules(self.locations.modules_data)

    def with_documents(self, documents: list[Document]):
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        self.db.add_texts(texts=texts, metadatas=metadatas)
        return self

    def with_modules(self, folder: Optional[Path] = None):
        if folder is None:
            folder = self.locations.modules_data
        documents = self.modules_to_documents(folder)
        return self.with_documents(documents)

    def with_papers(self, folder: Optional[Path] = None):
        if folder is None:
            folder = self.locations.papers
        documents = self.papers_to_documents(folder)
        return self.with_documents(documents)

    def with_papers_incremental(self, folder: Optional[Path] = None, persist_interval: Optional[int] = 10):
        if folder is None:
            folder = self.locations.papers
        papers = traverse(folder, lambda p: "pdf" in p.suffix)
        print(f"indexing {len(papers)} papers")
        loaders = [UnstructuredPDFLoader(str(p)) for p in papers]
        i = 1
        total_runs = len(loaders)
        if persist_interval is None:
            persist_interval = total_runs
        for loader in loaders:
            print(f"adding paper {i} out of {len(loaders)}")
            docs: list[Document] = loader.load()
            self.with_documents(docs)
            if i % persist_interval == 0 or i >= total_runs:
                self.db.persist()
            i = i + 1
        print("papers loading finished")
        return self

    def persist(self):
        self.db.persist()

    """
    def chroma_from_data(self,
                          papers: Optional[Path] = None,
                          modules: Optional[Path] = None,
                          persist_directory: Optional[Path] = None
                          ):
        modules_docs = self.modules_to_documents(modules) if modules is not None else []
        papers_docs = self.papers_to_documents(papers) if papers is not None else []
        documents = modules_docs + papers_docs
        directory = self.persist_directory if persist_directory is None else persist_directory
        if len(documents) == 0:
            print(f"both documents and modules are None, initializing empty Chroma")
            return Chroma(persist_directory=str(directory), embedding_function=self.embedding, collection_name=collection_name)
        else:
            sub_docs = self.splitter.split_documents(documents)
            return Chroma.from_documents(sub_docs, collection_name=collection_name)
    def load_default_index(self, with_papers: bool = True, with_modules: bool = True):
        print(f"loading default index with papers from {self.locations.papers} and modules from {self.locations.modules_data}")
        papers = self.locations.papers if with_papers else None
        modules = self.locations.modules_data if with_modules else None
        self.db = self.chroma_from_data(papers, modules)
        self.chain = self.make_chain()
    """



"""
def index(locations: Locations, load_modules: bool = True, load_papers: bool = True, temperature: float = 0.0):
    modules_loaders = [DataFrameLoader(pd.read_csv(tsv, sep="\t"), page_content_column="identifier") for tsv in with_ext(locations.modules_data, "tsv")] if load_modules else []
    pdf_loaders = make_paper_loaders(locations) if load_papers else []
    loaders = modules_loaders + pdf_loaders

    index = VectorstoreIndexCreator(vectorstore_kwargs={"persist_directory": str(locations.paper_index)}).from_loaders(loaders)
    print(f"indexing kind of finished, it will be saved to {locations.paper_index}")
    #apoe_result = index.query_with_sources("What do you know about APOE gene?")
    test_result = "MTHFR"
    print(index.query_with_sources(f"What is {test_result}?"))
    return index
"""
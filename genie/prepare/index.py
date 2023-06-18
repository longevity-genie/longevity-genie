from langchain.document_loaders import DataFrameLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.embeddings.base import Embeddings
from langchain.schema import Document
from langchain.text_splitter import TextSplitter
from langchain.vectorstores import Chroma
from pycomfort.files import *

from genie.sqlite import *
from genie.prepare.splitter import RecursiveSplitterWithSource


def _dataframe_to_document(df: pl.DataFrame) -> List[Document]:
    return DataFrameLoader(df.to_pandas(), page_content_column="text").load()

def db_with_documents(db: Chroma, documents: list[Document],
                      splitter: TextSplitter,
                      debug: bool = False,
                      id_field: Optional[str] = None):
    docs = splitter.split_documents(documents)
    texts = [doc.page_content for doc in docs]
    metadatas = [doc.metadata for doc in docs]
    ids = [doc.metadata[id_field] for doc in docs] if id_field is not None else None
    if debug:
        for doc in documents:
            print(f"ADD TEXT: {doc.page_content}")
            print(f"ADD METADATA {doc.metadata}")
    db.add_texts(texts=texts, metadatas=metadatas, ids = ids)
    return db


def write_db(persist_directory: Path,
             collection_name: str,
             documents: list[Document],
             chunk_size: int = 6000,
             debug: bool = False,
             id_field: Optional[str] = None,
             embeddings: Optional[Embeddings] = None):
    where = persist_directory / collection_name
    where.mkdir(exist_ok=True, parents=True)
    if embeddings is None:
        embeddings = OpenAIEmbeddings()
    db = Chroma(collection_name=collection_name, persist_directory=str(where), embedding_function=embeddings)
    splitter = RecursiveSplitterWithSource(chunk_size=chunk_size)
    splitter._chunk_size = chunk_size
    db_updated = db_with_documents(db, documents, splitter, debug, id_field)
    db_updated.persist()
    return where

"""
collection.query(
    query_embeddings=[[11.1, 12.1, 13.1],[1.1, 2.3, 3.2] ...]
    n_results=10,
    where={"metadata_field": "is_equal_to_this"},
    where_document={"$contains":"search_string"}
)
"""
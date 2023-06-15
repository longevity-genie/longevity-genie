import copy
from enum import Enum

from langchain import OpenAI
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import DataFrameLoader
from langchain.document_loaders import UnstructuredPDFLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from langchain.text_splitter import TextSplitter, RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from pycomfort.files import *

from genie.sqlite import *
from prepare.splitter import RecursiveSplitterWithSource


class Index:

    #locations: Locations
    persist_directory: Path
    embedding: OpenAIEmbeddings
    db: Chroma
    llm: ChatOpenAI
    chain: RetrievalQAWithSourcesChain
    splitter: TextSplitter
    model_name: str
    chain_type: str

    def __init__(self,
                 persist_directory: Path,
                 model_name: str = "gpt-3.5-turbo-16k",
                 chain_type: str = "stuff",
                 search_type: str = "similarity",
                 chunk_size: int = 1000,
                 k: Optional[int] = None
                 ): #, chroma_server: str = "0.0.0.0", chroma_port: str = "6000"
        self.persist_directory = persist_directory
        self.embedding = OpenAIEmbeddings()
        #settings = Settings(chroma_api_impl="rest", chroma_server_host=chroma_server, chroma_server_http_port=chroma_port)
        self.db = Chroma(persist_directory=str(self.persist_directory),
                         embedding_function=self.embedding #,client_settings=settings
                         )
        self.model_name = model_name
        self.splitter = RecursiveSplitterWithSource(chunk_size=chunk_size, chunk_overlap=200)
        self.chain_type = chain_type
        self.k = k
        self.chain = self.make_chain(self.chain_type, search_type=search_type) if k is not None and k > 0 else self.make_chain(self.chain_type, search_type=search_type)


    def make_chain(self, chain_type: str, search_type: str):
        self.llm = ChatOpenAI(model_name=self.model_name)
        #arch_kwargs = {"k": k} if self.k is not None and self.k > 0 else {}
        chain = RetrievalQAWithSourcesChain.from_chain_type(
            self.llm,
            retriever=self.db.as_retriever(search_type = search_type),
            chain_type=chain_type,
            verbose=True
        )
        if self.model_name == "gpt-4":
            chain.max_tokens_limit = chain.max_tokens_limit * 2
        chain.reduce_k_below_max_tokens = False #True
        return chain


    def query_with_sources(self, question: str,  previous_dialog: list[str]):
        #TODO process previous dialog
        return self.chain({self.chain.question_key: question})

    #def query_without_sources(self, question: str):
    #    return self.chain({self.chain.question_key: question})

    def modules_to_documents(self, folder: Path): #OLD
        modules = with_ext(folder, "tsv").to_list() if folder.is_dir() else seq([folder])
        print(f"detected text for the following modules {modules}")
        modules_loaders = [DataFrameLoader(pd.read_csv(tsv, sep="\t")) for tsv in modules]
        print(f"indexing {len(modules_loaders)} modules")
        modules_docs = seq([loader.load() for loader in modules_loaders]).flatten().to_list()
        return modules_docs

    def dataframe_to_document(df: pl.DataFrame) -> List[Document]:
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

    def with_modules(self, folder: Path):
        #if folder is None:
        #    folder = self.locations.modules_text_data
        documents = self.modules_to_documents(folder)
        print(f"indexing modules from {folder}, {len(documents)} documents found!")
        return self.with_documents(documents)


    def with_paper(self, paper: Path):
        loader = UnstructuredPDFLoader(str(paper))
        docs: list[Document] = loader.load()
        self.with_documents(docs)
        return self


    def persist(self):
        self.db.persist()
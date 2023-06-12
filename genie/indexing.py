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

class RecursiveSplitterWithSource(RecursiveCharacterTextSplitter):
    def create_documents(
            self, texts: List[str], metadatas: Optional[List[dict]] = None
    ) -> List[Document]:
        """Create documents from a list of texts."""
        _metadatas = metadatas or [{}] * len(texts)
        documents = []
        for i, text in enumerate(texts):
            meta = _metadatas[i]
            source: Optional[str] = meta["source"] if "source" in meta else None
            for j, chunk in enumerate(self.split_text(text)):
                new_meta = copy.deepcopy(meta)
                if source is not None:
                    new_meta["source"] = source + "#" + str(j)
                new_doc = Document(
                    page_content=chunk, metadata=new_meta
                )
                documents.append(new_doc)
        return documents

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
                 model_name: str = "gpt-3.5-turbo",
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


    def with_documents(self, documents: list[Document],
                       debug: bool = False,
                       id_field: Optional[str] = None):
        docs = self.splitter.split_documents(documents)
        texts = [doc.page_content for doc in docs]
        metadatas = [doc.metadata for doc in docs]
        ids = [doc.metadata[id_field] for doc in docs] if id_field is not None else None
        if debug:
            for doc in documents:
                print(f"ADD TEXT: {doc.page_content}")
                print(f"ADD METADATA {doc.metadata}")
        self.db.add_texts(texts=texts, metadatas=metadatas, ids = ids)
        return self

    def with_modules(self, folder: Path):
        #if folder is None:
        #    folder = self.locations.modules_text_data
        documents = self.modules_to_documents(folder)
        print(f"indexing modules from {folder}, {len(documents)} documents found!")
        return self.with_documents(documents)

    def with_papers(self, folder: Optional[Path] = None, proofread: bool = False):
        #if folder is None:
        #    folder = self.locations.papers
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
        return self.with_documents(docs, id_field="source")

    def with_paper(self, paper: Path):
        loader = UnstructuredPDFLoader(str(paper))
        docs: list[Document] = loader.load()
        self.with_documents(docs)
        return self


    def with_papers_incremental(self, folder: Path, persist_interval: Optional[int] = 10, ):
        #if folder is None:
        #    folder = self.locations.papers
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
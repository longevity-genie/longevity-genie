import os
from typing import Optional

import loguru
from chromadb.api import Embeddings
from indexpaper.resolvers import Device
from langchain import LLMChain, BasePromptTemplate
from langchain.callbacks.base import Callbacks
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chains.chat_vector_db.prompts import CONDENSE_QUESTION_PROMPT
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import HuggingFaceBgeEmbeddings, HuggingFaceEmbeddings
from langchain.embeddings import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.vectorstores import Qdrant
from pycomfort.config import load_environment_keys
from qdrant_client import QdrantClient


# from genie.chats import ChatIndex, GenieChain, ChainType

token_limits = {
    "gpt-4-32k": 32768,
    "gpt-4": 8192,
    "gpt-3.5-turbo-16k": 16384,
    "gpt-3.5-turbo": 4096,
    "other": 4096
}


class Genie:

    collections: list[str]
    client: QdrantClient
    memory: ConversationBufferMemory
    collections: list[str]
    db: Qdrant
    chain: RetrievalQAWithSourcesChain
    verbose: bool

    def guess_embeddings_from_collection_name(self, collection_name: str, device: str = "cpu", normalize_embeddings: bool = True) -> Embeddings:
        encode_kwargs = {'normalize_embeddings': normalize_embeddings}
        model_kwargs = {'device': device}
        if "bge_large" in collection_name:
            model_name = "BAAI/bge-large-en"
            return HuggingFaceBgeEmbeddings(
                model_name=model_name,
                model_kwargs=model_kwargs,
                encode_kwargs=encode_kwargs
            )
        elif "biolinkbert_large" in collection_name:
            model_name = "michiyasunaga/BioLinkBERT-large"
            return HuggingFaceEmbeddings(model_name = model_name,
                                         model_kwargs=model_kwargs,
                                         encode_kwargs=encode_kwargs)
        elif "openai" in collection_name or "ada" in collection_name:
            return OpenAIEmbeddings()
        else:
            loguru.logger.error(f"cannot decide on embeddings for {collection_name} using bge-large-end by default")
            model_name = "BAAI/bge-large-en"
            return HuggingFaceBgeEmbeddings(
                model_name=model_name,
                model_kwargs=model_kwargs,
                encode_kwargs=encode_kwargs
            )

    def make_chain(self,
                   condense_question_prompt: BasePromptTemplate = CONDENSE_QUESTION_PROMPT,
                   callbacks: Callbacks = None):

        doc_chain = load_qa_with_sources_chain(self.llm, "stuff", verbose=self.verbose, callbacks=callbacks)

        condense_question_chain = LLMChain(
            llm=self.llm,
            prompt=condense_question_prompt,
            verbose=self.verbose,
            callbacks=callbacks,
        )


        result = ConversationalRetrievalChain(
            retriever=self.db.as_retriever(),
            combine_docs_chain=doc_chain,
            question_generator=condense_question_chain,
            callbacks=callbacks,
            return_source_documents = True,
            return_generated_question = True
        )
        result.memory = self.memory
        result.get_chat_history = lambda v: str(self.memory.chat_memory.messages)
        return result


    def __init__(self,
                 db: Optional[str] = "https://5bea7502-97d4-4876-98af-0cdf8af4bd18.us-east-1-0.aws.cloud.qdrant.io:6333",
                 default_model = "gpt-3.5-turbo-16k",
                 collection_name: str = "bge_large_512_moskalev_papers_paragraphs",
                 device = Device.cpu,
                 verbose: bool = True
                 ):
        openai = load_environment_keys(usecwd=True)
        url = db if db is not None else os.getenv("db")
        self.client = QdrantClient(
            url=url,
            port=6333,
            grpc_port=6334,
            prefer_grpc=True,
            api_key=os.getenv("QDRANT_KEY")
        )
        self.verbose = verbose
        self.memory = ConversationBufferMemory(memory_key="chat_history")
        self.collections = [c.name for c in self.client.get_collections().collections]
        self.collection_name = collection_name
        self.llm = ChatOpenAI(model = default_model)
        self.update_db(collection_name)


    def update_db(self, collection_name: str):
        embeddings = self.guess_embeddings_from_collection_name(self.collection_name)
        self.db = Qdrant(self.client, collection_name=collection_name, embeddings=embeddings)
        self.chain = self.make_chain()
        return self.db, self.chain

    def message(self, message: str):
        return self.chain(message)

    @property
    def history(self) -> list[dict]:
        return [ {
            "content": message.content,
            "type": message.type
            } for message in self.memory.chat_memory.messages
        ]




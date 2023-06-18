
import os
from enum import Enum
from pathlib import Path
from typing import Optional

import dotenv
from dotenv import load_dotenv
from langchain import BasePromptTemplate
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chains.base import Chain
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.chat_models.base import BaseChatModel
from langchain.embeddings import OpenAIEmbeddings
from langchain.embeddings.base import Embeddings
from langchain.vectorstores import Chroma


class ChainType(Enum):
    Stuff = "stuff"
    MapReduce = "map_reduce"
    Refine = "refine"
    MapRerank = "map_rerank"


class Chains:

    embeddings: Embeddings
    model_name: str
    llm: BaseChatModel
    modules: RetrievalQAWithSourcesChain
    papers: RetrievalQAWithSourcesChain

    def __init__(self, indexes: Path,
                 model_name: str = "gpt-3.5-turbo-16k",
                 retrieval_chain_type: ChainType = ChainType.Stuff,
                 embeddings: Optional[Embeddings] = None):
        self.model_name = model_name
        self.retrieval_chain_type = retrieval_chain_type
        if embeddings is None:
            self.embeddings = OpenAIEmbeddings()
        else:
            self.embeddings = embeddings
        llm = ChatOpenAI(model_name=self.model_name)
        self.modules = self.make_retrieval_chain(indexes, "modules", llm, self.embeddings, ChainType.Stuff)
        self.papers = self.make_retrieval_chain(indexes, "papers", llm, self.embeddings, ChainType.Stuff)


    def make_retrieval_chain(self,
                             indexes: Path,
                             name: str,
                             llm: BaseChatModel,
                             embeddings: Embeddings,
                             retrieval_chain_type: ChainType = ChainType.Stuff) -> RetrievalQAWithSourcesChain:
        """
        Creates a chain to retrieve data from index store
        :param indexes:
        :param name:
        :param llm:
        :param retrieval_chain_type:
        :return:
        """
        where = indexes / name
        assert where.exists(), f"{name} folder {where} does not exist!"
        modules_db = Chroma(collection_name="modules",
                             persist_directory=str(where),
                             embedding_function=embeddings)
        return RetrievalQAWithSourcesChain.from_chain_type(
            llm,
            retriever=modules_db.as_retriever(),
            chain_type=retrieval_chain_type.value
        )


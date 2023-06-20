
import os
from enum import Enum
from pathlib import Path
from typing import Optional

import dotenv
from dotenv import load_dotenv
from langchain import BasePromptTemplate, LLMChain
from langchain.base_language import BaseLanguageModel
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chains.base import Chain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain.chains.qa_with_sources import stuff_prompt
from langchain.chains.qa_with_sources.base import BaseQAWithSourcesChain
from langchain.chat_models import ChatOpenAI
from langchain.chat_models.base import BaseChatModel
from langchain.embeddings import OpenAIEmbeddings
from langchain.embeddings.base import Embeddings
from langchain.vectorstores import Chroma
from genie.wishes.genetic import genetic_source_template

def make_stuff_chain(llm: BaseLanguageModel, wish: BasePromptTemplate = stuff_prompt.PROMPT, verbose: bool = True):
    document_prompt: BasePromptTemplate = stuff_prompt.EXAMPLE_PROMPT
    document_variable_name: str = "summaries"
    llm_chain = LLMChain(llm=llm, prompt=wish, verbose=verbose)
    return StuffDocumentsChain(
        llm_chain=llm_chain,
        document_variable_name=document_variable_name,
        document_prompt=document_prompt,
        verbose=verbose
    )

def make_indexed_chain(indexes: Path, name: str, llm: BaseChatModel, embeddings: Embeddings, wish: BasePromptTemplate, verbose: bool = False):
    """
    Creates a chain to retrieve data from index store
    :param indexes:
    :param name:
    :param llm:
    :param embeddings:
    :type wish: object
    :return:
    """
    where = indexes / name
    assert where.exists(), f"{name} folder {where} does not exist!"
    modules_db = Chroma(collection_name=name,
                        persist_directory=str(where),
                        embedding_function=embeddings)
    stuff = make_stuff_chain(llm=llm, wish=wish, verbose=verbose)
    return RetrievalQAWithSourcesChain(combine_documents_chain=stuff, retriever=modules_db.as_retriever())


class ChainType(Enum):
    Stuff = "stuff"
    MapReduce = "map_reduce"
    Refine = "refine"
    MapRerank = "map_rerank"

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
    :param embeddings:
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
        #self.modules = make_retrieval_chain(indexes, "modules", llm, self.embeddings, ChainType.Stuff)
        #self.papers = make_retrieval_chain(indexes, "papers", llm, self.embeddings, ChainType.Stuff)

        #self.modules = make_alternative_source_chain(indexes, "modules", llm, self.embeddings, prompt=genetic_source_template)
        #self.papers  = make_alternative_source_chain(indexes, "papers", llm, self.embeddings)




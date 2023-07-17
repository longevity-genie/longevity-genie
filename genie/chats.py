import os
from enum import Enum
from pathlib import Path

import dotenv
from dotenv import load_dotenv
from langchain import BasePromptTemplate
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.chains.base import Chain
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

from genie.chains import ChainType

token_limits = {
    "gpt-4-32k": 32768,
    "gpt-4": 8192,
    "gpt-3.5-turbo-16k": 16384,
    "gpt-3.5-turbo": 4096,
    "other": 4096
}

from agent import get_trials_reasons, calculate_trials_statistics

class GenieChain(Enum):
    IndexSource = 'IndexSource'
    Chat = 'Chat'
    Agent = 'Agent'
    Advanced = 'Advanced'



class ChatIndex:
    """
    This class is outdated, it will be rewritten after chains will be tested
    """

    username: str
    vector_store: Chroma
    persist_directory: Path
    model_name: str
    genie_chain: GenieChain
    chat_chain: Chain #BaseConversationalRetrievalChain #ConversationalRetrievalChain
    chain_type: ChainType.MapReduce
    search_type: str
    chat_history: list[(str, str)]
    messages: list[str]
    llm: ChatOpenAI
    question_prompt: BasePromptTemplate

    def __init__(self,
                 persist_directory: Path,
                 username: str = "Zuzalu user",
                 model_name: str = "gpt-3.5-turbo-16k",
                 genie_chain: GenieChain = GenieChain.IndexSource,
                 chain_type: ChainType = ChainType.MapReduce,
                 search_type: str = "similarity"
                 ):
        e = dotenv.find_dotenv()
        has_env: bool = load_dotenv(e, verbose=True, override=True)
        if not has_env:
            print("Did not found environment file, using system OpenAI key (if exists)")
        openai_key = os.getenv('OPENAI_API_KEY')
        print(f"THE KEY IS: {openai_key}")
        self.username = username
        self.model_name = model_name
        self.embedding = OpenAIEmbeddings()
        self.persist_directory = persist_directory
        self.vector_store = Chroma(persist_directory=str(self.persist_directory),
                         embedding_function=self.embedding)
        self.llm = ChatOpenAI(model_name=self.model_name)
        self.chat_history = []
        self.messages = []
        self.search_type = search_type
        self.genie_chain = genie_chain
        self.chain_type = chain_type

        self.chat_chain = self.make_chain(genie_chain, chain_type, search_type)

    def _make_conversation_chain(self, chain_type: ChainType, search_type: str):
        return ConversationalRetrievalChain.from_llm(
            self.llm,
            self.vector_store.as_retriever(search_type = search_type),
            chain_type=chain_type.value
        )


    def _index_make_chain(self, chain_type: ChainType, search_type: str):
        self.llm = ChatOpenAI(model_name=self.model_name)
        chain = RetrievalQAWithSourcesChain.from_chain_type(
            self.llm,
            retriever=self.vector_store.as_retriever(search_type = search_type),
            chain_type=chain_type.value
        )
        if self.model_name in token_limits:
            chain.max_tokens_limit = token_limits[self.model_name]
        else:
            chain.max_tokens_limit = token_limits["other"]
        chain.reduce_k_below_max_tokens = False #True
        return chain

    def make_chain(self,
                   genie_chain: GenieChain = GenieChain.IndexSource,
                   chain_type: ChainType = ChainType.MapReduce,
                   search_type: str = "similarity"):
        if genie_chain == GenieChain.IndexSource:
            print("initializing index chain")
            return self._index_make_chain(chain_type, search_type)
        elif genie_chain == GenieChain.Chat:
            print("initializing conversation chain")
            return self._make_conversation_chain(chain_type, search_type)
        else:
            print("initializing index chain")
            return self._index_make_chain(chain_type, search_type)

    def with_updated_chain(self, genie_chain: GenieChain, chain_type: ChainType, search_type: str):
        self.chat_chain = self.make_chain(genie_chain, chain_type, search_type)
        return self

    def answer(self, question: str):
        result = self.chat_chain({"question": question, "chat_history": self.chat_history})
        print(f"RESULT OUTPUT is {result}")
        self.chat_history = [(question, result["answer"])]
        full_answer = f"""{result["answer"]}\nSOURCES: "{result["sources"]}"""
        self.messages = self.messages + [question, full_answer]
        return result["answer"]


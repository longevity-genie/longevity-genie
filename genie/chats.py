import os
from pathlib import Path
from typing import Dict

import dotenv
import weaviate
from dotenv import load_dotenv
from langchain import OpenAI, BasePromptTemplate
from langchain.chains import ChatVectorDBChain
from langchain.chains.base import Chain
from langchain.chains.conversational_retrieval.base import BaseConversationalRetrievalChain, \
    ConversationalRetrievalChain
from langchain.chains.conversational_retrieval.prompts import CONDENSE_QUESTION_PROMPT
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Weaviate, Chroma


class ChatIndex:

    username: str
    vector_store: Chroma
    persist_directory: Path
    model_name: str
    chat_chain: Chain #BaseConversationalRetrievalChain #ConversationalRetrievalChain
    chat_history: list[(str, str)]
    messages: list[str]

    def __init__(self,
                 persist_directory: Path,
                 username: str = "Zuzalu user",
                 model_name: str = "gpt-3.5-turbo",
                 chain_type: str = "map_reduce",
                 search_type: str = "mmr"
                 #host: str = "0.0.0.0", port: str = "8006"
                 ):
        question_prompt: BasePromptTemplate = CONDENSE_QUESTION_PROMPT
        e = dotenv.find_dotenv()
        has_env: bool = load_dotenv(e, verbose=True)
        if not has_env:
            print("Did not found environment file, using system OpenAI key (if exists)")
        openai_key = os.getenv('OPENAI_API_KEY')
        print(f"THE KEY IS: {openai_key}")
        self.username = username
        self.model_name = model_name
        self.embedding = OpenAIEmbeddings()
        self.persist_directory = persist_directory
        self.vector_store = Chroma(persist_directory=str(self.persist_directory),
                         embedding_function=self.embedding #,client_settings=settings
                         )
        self.llm = OpenAI(model_name=self.model_name)
        self.chat_chain = ConversationalRetrievalChain.from_llm(
            self.llm,
            self.vector_store.as_retriever(search_type = search_type),
            condense_question_prompt=question_prompt,
            chain_type=chain_type
        )
        self.chat_history = []
        self.messages = []

    def answer(self, question: str):
        result = self.chat_chain({"question": question, "chat_history": self.chat_history})
        print(f"RESULT OUTPUT is {result}")
        self.chat_history = [(question, result["answer"])]
        self.messages = self.messages + [question, result["answer"]]
        return result["answer"]


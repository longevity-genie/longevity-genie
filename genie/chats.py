import os
from typing import Dict

import dotenv
import weaviate
from dotenv import load_dotenv
from langchain import OpenAI
from langchain.chains import ChatVectorDBChain
from langchain.chains.conversational_retrieval.base import BaseConversationalRetrievalChain
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Weaviate


class ChatIndex:

    client: weaviate.Client
    vectorstore: Weaviate
    model_name: str
    chat_chain: BaseConversationalRetrievalChain
    chat_history: list[(str, str)]
    messages: list[str]

    def _default_schema(self, index_name: str) -> Dict:
        return {
            "class": index_name,
            "properties": [
                {
                    "name": "text",
                    "dataType": ["text"],
                }
            ],
        }


    def __init__(self, model_name: str = "gpt-3-turbo", host: str = "0.0.0.0", port: str = "8006"):
        e = dotenv.find_dotenv()
        has_env: bool = load_dotenv(e, verbose=True)
        if not has_env:
            print("Did not found environment file, using system OpenAI key (if exists)")
        self.model_name = model_name
        openai_key = os.getenv('OPENAI_API_KEY')
        self.embedding = OpenAIEmbeddings()
        self.client = weaviate.Client(f"http://{host}:{port}",
            additional_headers={
            "X-OpenAI-Api-Key": openai_key}
        )
        from weaviate.util import get_valid_uuid
        schema = self._default_schema("Longevity")
        #attributes = list(metadatas[0].keys()) if metadatas else None
        if not self.client.schema.contains(schema):
            self.client.schema.create_class(schema)
        self.vector_store = Weaviate(self.client, "text2vec-openai", "content")
        self.llm = OpenAI(model_name=self.model_name)
        self.chat_chain = ChatVectorDBChain.from_llm(self.llm, self.vector_store)
        self.chat_history = []
        self.messages = []

    def answer(self, question: str):
        result = self.chat_chain({"question": question, "chat_history": self.chat_history})
        self.chat_history = [(question, result["answer"])]
        self.messages = self.messages + [question, result["answer"]]
        return result["answer"]


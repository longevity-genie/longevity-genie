import dataclasses
import os
from enum import Enum
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
from langchain.schema import Document
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

@dataclasses.dataclass
class WishAnswer:

    sources_documents: list[Document]
    question: str
    generated_question: str
    answer: str

    def doc_to_json(self, d: Document, fields: list[str]):
        result = {f: d.metadata[f] for f in fields if f in d.metadata}
        result["page_content"] = d.page_content
        return result

    def json_sources(self):
        return [self.doc_to_json(d, ["source", "doi", "annotations_title", "externalids_pubmed"]) for d in self.sources_documents]

    @staticmethod
    def from_dict(dic: dict):
        return WishAnswer(
            sources_documents = dic["source_documents"],
            question = dic["question"],
            generated_question = dic["generated_question"],
            answer = dic["answer"]
        )


class ChainType(Enum):
    Stuff = "stuff"
    MapReduce = "map_reduce"
    Refine = "refine"
    MapRerank = "map_rerank"

class SearchType(Enum):
    similarity = "similarity"
    mmr = "mmr"

class Genie:

    collections: list[str]
    client: QdrantClient
    memory: ConversationBufferMemory
    collections: list[str]
    db: Qdrant
    chain: RetrievalQAWithSourcesChain
    verbose: bool


    def fix_langchain_memory_bug(self):
        """
        temporal workaround according to https://github.com/langchain-ai/langchain/issues/2256
        :return:
        """
        import langchain
        from typing import Dict, Any, Tuple
        from langchain.memory.utils import get_prompt_input_key

        def _get_input_output(
                self, inputs: Dict[str, Any], outputs: Dict[str, str]
        ) -> Tuple[str, str]:
            if self.input_key is None:
                prompt_input_key = get_prompt_input_key(inputs, self.memory_variables)
            else:
                prompt_input_key = self.input_key
            if self.output_key is None:
                output_key = list(outputs.keys())[0]
            else:
                output_key = self.output_key
            return inputs[prompt_input_key], outputs[output_key]

        langchain.memory.chat_memory.BaseChatMemory._get_input_output = _get_input_output

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
                   k: int, score_threshold: float, chain_type: ChainType, search_type: SearchType,
                   condense_question_prompt: BasePromptTemplate = CONDENSE_QUESTION_PROMPT,
                   callbacks: Callbacks = None):
        """
        :param search_type: similarity or mmr
        :param k: number of documents retrieveed by retriever
        :param condense_question_prompt: if we need to reformulate question taking chat into condieration
        :param callbacks:
        :return:
        """

        doc_chain = load_qa_with_sources_chain(self.llm, chain_type.value, verbose=self.verbose, callbacks=callbacks)

        condense_question_chain = LLMChain(
            llm=self.llm,
            prompt=condense_question_prompt,
            verbose=self.verbose,
            callbacks=callbacks,
        )


        result = ConversationalRetrievalChain(
            retriever=self.db.as_retriever(search_type=search_type.value, search_kwargs={'k': k, 'score_threshold': score_threshold}),
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
                 chain_type: ChainType = ChainType.Stuff,
                 search_type: SearchType = SearchType.similarity,
                 k: int = 10,
                 score_threshold: float = 0.05,
                 device = Device.cpu,
                 verbose: bool = True
                 ):
        self.fix_langchain_memory_bug()
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
        self.update_db(collection_name, k, score_threshold,  chain_type, search_type)


    def update_db(self, collection_name: str, k: int, score_threshold: float, chain_type: ChainType, search_type: SearchType):
        embeddings = self.guess_embeddings_from_collection_name(self.collection_name)
        self.db = Qdrant(self.client, collection_name=collection_name, embeddings=embeddings)
        self.chain = self.make_chain(k, score_threshold, chain_type, search_type)
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




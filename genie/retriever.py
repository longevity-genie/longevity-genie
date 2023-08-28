import collections
import dataclasses
import os
from collections import OrderedDict
from typing import Optional, OrderedDict, Any

import loguru
from chromadb.api import Embeddings
from functional import seq
from langchain.callbacks.manager import CallbackManagerForRetrieverRun, AsyncCallbackManagerForRetrieverRun
from langchain.embeddings import HuggingFaceBgeEmbeddings, HuggingFaceEmbeddings
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document, BaseRetriever
from langchain.vectorstores import Qdrant
from longdata.agent_router_chain import AgentRouterChain
from qdrant_client import QdrantClient

from pycomfort.config import load_environment_keys
from genie.enums import SearchType


# from genie.chats import ChatIndex, GenieChain, ChainType

@dataclasses.dataclass
class RetrieverInfo:
    name: str
    retriever: BaseRetriever
    weight: float = 1.0


class GenieRetriever(BaseRetriever):
    """Retriever that ensembles the multiple retrievers.

   It uses a rank fusion.

   Args:
       retrievers: A list of retrievers to ensemble.
       weights: A list of weights corresponding to the retrievers. Defaults to equal
           weighting for all retrievers.
       c: A constant added to the rank, controlling the balance between the importance
           of high-ranked items and the consideration given to lower-ranked items.
           Default is 60.
   """
    databases: OrderedDict[str, Qdrant]
    retrievers: list[RetrieverInfo] = []
    all_collections: list[str] = []
    c: int = 60
    agents: Optional[list] = None


    def _get_relevant_documents(
            self,
            query: str,
            *,
            run_manager: CallbackManagerForRetrieverRun,
    ) -> list[Document]:
        """
        Get the relevant documents for a given query.

        Args:
            query: The query to search for.

        Returns:
            A list of reranked documents.
        """

        # Get fused result of the retrievers.
        fused_documents = self.rank_fusion(query, run_manager)
        if self.agents is not None:
            for agent in self.agents:
                result = agent(query)
                answer = result['output']
                steps = "INTERMEDIATE STEPS TO DEDUCE ANSWER: " + str(result['intermediate_steps'])
                dictionary = {
                    "title": "agent_result",
                    #"intermediate_steps": steps,
                    "source": "AGENT_THINKING"
                }
                doc = Document( page_content = answer, metadata = dictionary)
                fused_documents.append(doc)

        return fused_documents

    async def _aget_relevant_documents(
            self,
            query: str,
            *,
            run_manager: AsyncCallbackManagerForRetrieverRun,
    ) -> list[Document]:
        """
        Asynchronously get the relevant documents for a given query.

        Args:
            query: The query to search for.

        Returns:
            A list of reranked documents.
        """

        # Get fused result of the retrievers.
        fused_documents = await self.arank_fusion(query, run_manager)

        return fused_documents

    def rank_fusion(
            self, query: str, run_manager: CallbackManagerForRetrieverRun
    ) -> list[Document]:
        """
        Retrieve the results of the retrievers and use rank_fusion_func to get
        the final result.

        Args:
            query: The query to search for.

        Returns:
            A list of reranked documents.
        """

        # Get the results of all retrievers.
        retriever_docs = []
        for info in self.retrievers:
            docs = info.retriever.get_relevant_documents(query, callbacks=run_manager.get_child(tag=info.name))
            for doc in docs:
                doc.metadata["retriever"] = info.name
                if isinstance(doc.metadata['annotations_title'], list):
                    title = doc.metadata['annotations_title'][0] if doc.metadata['annotations_title'] else "No title found"
                elif doc.metadata['annotations_title'] is None:
                    title = "No title found"
                else:
                    title = doc.metadata['annotations_title']
                title = title + " (" + doc.metadata["retriever"] + ")"
                doc.metadata["title"] = title
            retriever_docs.append(docs)

        # apply rank fusion
        fused_documents = self.weighted_reciprocal_rank(retriever_docs)

        return fused_documents

    async def arank_fusion(
            self, query: str, run_manager: AsyncCallbackManagerForRetrieverRun
    ) -> list[Document]:
        """
        Asynchronously retrieve the results of the retrievers
        and use rank_fusion_func to get the final result.

        Args:
            query: The query to search for.

        Returns:
            A list of reranked documents.
        """

        retriever_docs = []
        for info in self.retrievers:
            docs = await info.retriever.aget_relevant_documents(query, callbacks=run_manager.get_child(tag=info.name))
            for d in docs:
                d.metadata["retriever"] = info.name
            retriever_docs.append(docs)

        # apply rank fusion
        fused_documents = self.weighted_reciprocal_rank(retriever_docs)

        return fused_documents

    @property
    def weights(self) -> list[float]:
        sum_weights: float = seq(self.retrievers).sum(lambda i: i.weight)
        return [i.weight / sum_weights for i in self.retrievers]

    def weighted_reciprocal_rank(
            self, doc_lists: list[list[Document]]
    ) -> list[Document]:
        """
        Perform weighted Reciprocal Rank Fusion on multiple rank lists.
        You can find more details about RRF here:
        https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf

        Args:
            doc_lists: A list of rank lists, where each rank list contains unique items.

        Returns:
            list: The final aggregated list of items sorted by their weighted RRF
                    scores in descending order.
        """

        # Create a union of all unique documents in the input doc_lists
        all_documents = set()
        for doc_list in doc_lists:
            for doc in doc_list:
                all_documents.add(doc.page_content)

        # Initialize the RRF score dictionary for each document
        rrf_score_dic = {doc: 0.0 for doc in all_documents}

        # Calculate RRF scores for each document
        for doc_list, weight in zip(doc_lists, self.weights):
            for rank, doc in enumerate(doc_list, start=1):
                rrf_score = weight * (1 / (rank + self.c))
                rrf_score_dic[doc.page_content] += rrf_score

        # Sort documents by their RRF scores in descending order
        sorted_documents = sorted(
            rrf_score_dic.keys(), key=lambda x: rrf_score_dic[x], reverse=True
        )

        # Map the sorted page_content back to the original document objects
        page_content_to_doc_map = {
            doc.page_content: doc for doc_list in doc_lists for doc in doc_list
        }
        sorted_docs = [
            page_content_to_doc_map[page_content] for page_content in sorted_documents
        ]

        return sorted_docs

    @classmethod
    def from_collections(cls,
                 collection_names: Optional[list[str]] = None,
                 url: Optional[str] = None,
                 k: int = 4, search_type: SearchType = SearchType.similarity, score_threshold: float = 0.09,
                 agents: Optional[list[AgentRouterChain]] = None, #ugly but we have to integrate it fast
                 **kwargs: Any):
        load_environment_keys(usecwd=True)
        env_db = os.getenv("DATABASE_URL")
        if url is None:
            if env_db is None:
                loguru.logger.error(f"URL is none and DATABASE_URL environment variable is not set, using default value instead")
                url = "https://5bea7502-97d4-4876-98af-0cdf8af4bd18.us-east-1-0.aws.cloud.qdrant.io:6333"
            else:
                url = env_db
        client = QdrantClient(
            url=url,
            port=6333,
            grpc_port=6334,
            prefer_grpc=True,
            api_key=os.getenv("QDRANT_KEY")
        )
        all_collections = [c.name for c in client.get_collections().collections]
        if collection_names is None:
            collection_names = all_collections
        databases: OrderedDict[str, Qdrant] = collections.OrderedDict([
            (collection_name, Qdrant(client,
                                         collection_name=collection_name,
                                         embeddings=cls.guess_embeddings_from_collection_name(collection_name)
                                         )
                 ) for collection_name in collection_names]
        )
        return cls(databases = databases, all_collections = all_collections, agents = agents, **kwargs).with_updated_retrievers(k, search_type, score_threshold)

    @staticmethod
    def compute_retrievers(databases: OrderedDict[str, Qdrant],
                           k: int = 20,
                           search_type: SearchType = SearchType.similarity,
                           score_threshold: float = 0.05, collection_names: Optional[list[str]] = None):
        dbs = databases if collection_names is None else collections.OrderedDict([ (c, db) for c, db in databases.items() if c in collection_names])
        search_kwargs={'k': k, 'score_threshold': score_threshold}
        return [RetrieverInfo(
            name = c,
            retriever=db.as_retriever(search_type=search_type.value, search_kwargs=search_kwargs),
            weight=1.0) for c, db in dbs.items()]

    def with_updated_retrievers(self, k: int = 20, search_type: SearchType = SearchType.similarity, score_threshold: float = 0.05, collection_names: Optional[list[str]] = None):
        self.retrievers = self.compute_retrievers(self.databases, k, search_type, score_threshold, collection_names)
        return self


    @staticmethod
    def guess_embeddings_from_collection_name(collection_name: str, device: str = "cpu", normalize_embeddings: bool = True) -> Embeddings:
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
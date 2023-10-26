from typing import Optional

from langchain.chains import LLMChain
from langchain.schema.prompt_template import BasePromptTemplate
from langchain.callbacks.base import Callbacks
from langchain.chains.chat_vector_db.prompts import CONDENSE_QUESTION_PROMPT
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.schema import BaseRetriever
from pycomfort.config import load_environment_keys
from genie.enums import ChainType, SearchType


class GenieChat:

    retriever: BaseRetriever
    memory: ConversationBufferMemory
    chain: ConversationalRetrievalChain
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

    def make_chain(self, chain_type: ChainType = ChainType.Stuff,
                   condense_question_prompt: BasePromptTemplate = CONDENSE_QUESTION_PROMPT,
                   callbacks: Callbacks = None):
        """
        :param chain_type:
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
            retriever=self.retriever,
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
                 retriever: BaseRetriever,
                 default_model = "gpt-3.5-turbo-16k",
                 compression: bool = False,
                 verbose: bool = True
                 ):
        self.fix_langchain_memory_bug()
        openai = load_environment_keys(usecwd=True)
        self.llm = ChatOpenAI(model = default_model)
        self._retriever = retriever
        self.compress(compression)
        self.verbose = verbose
        self.memory = ConversationBufferMemory(memory_key="chat_history")
        self.chain = self.make_chain()

    def compress(self, compression: bool):
        if compression:
            compressor = LLMChainExtractor.from_llm(self.llm)
            compression_retriever = ContextualCompressionRetriever(base_compressor=compressor, base_retriever=self._retriever)
            self.retriever = compression_retriever
        else:
            self.retriever = self._retriever

    def message(self, message: str):
        return self.chain(message)

    @property
    def history(self) -> list[dict]:
        return [ {
            "content": message.content,
            "type": message.type
            } for message in self.memory.chat_memory.messages
        ]




import dataclasses

from langchain.schema import Document


# from genie.chats import ChatIndex, GenieChain, ChainType
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
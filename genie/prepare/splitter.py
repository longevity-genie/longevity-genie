from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pycomfort.files import *

from genie.sqlite import *
from copy import deepcopy

class RecursiveSplitterWithSource(RecursiveCharacterTextSplitter):
    """
    Splitter that also modifies metadata
    """
    def create_documents(
            self, texts: List[str], metadatas: Optional[List[dict]] = None
    ) -> List[Document]:
        """Create documents from a list of texts."""
        _metadatas = metadatas or [{}] * len(texts)
        documents = []
        for i, text in enumerate(texts):
            meta = _metadatas[i]
            source: Optional[str] = meta["source"] if "source" in meta else None
            for j, chunk in enumerate(self.split_text(text)):
                new_meta = deepcopy(meta)
                if source is not None:
                    new_meta["source"] = source + "#" + str(j)
                new_doc = Document(
                    page_content=chunk, metadata=new_meta
                )
                documents.append(new_doc)
        return documents


from pathlib import Path
from typing import Optional, List

from langchain.document_loaders import UnstructuredPDFLoader
from langchain.schema import Document
from pycomfort.files import traverse


def papers_to_documents(folder: Path, proofread: bool = False):
    txt = traverse(folder, lambda p: "txt" in p.suffix)
    texts = [t for t in txt if "_proofread.txt" in t.name] if proofread else txt
    docs: List[Document] = []
    for t in texts:
        doi = f"http://doi.org/{t.parent.name}/{t.stem}"
        with open(t, 'r') as file:
            text = file.read()
            if len(text)<10:
                print("TOO SHORT TEXT")
            else:
                doc = Document(
                    page_content = text,
                    metadata={"source": doi}
                )
                docs.append(doc)
    return docs

def parse_papers(folder: Optional[Path] = None, skip_existing: bool = True):
    papers: list[Path] = traverse(folder, lambda p: "pdf" in p.suffix)
    print(f"indexing {len(papers)} papers")
    i = 1
    max = len(papers)
    for p in papers:
        loader = UnstructuredPDFLoader(str(p))
        print(f"adding paper {i} out of {max}")
        docs: list[Document] = loader.load()
        if len(docs) ==1:
            f = p.parent / f"{p.stem}.txt"
            print(f"writing {f}")
            f.write_text(docs[0].page_content)
        else:
            for i, doc in enumerate(docs):
                f = (p.parent / f"{p.stem}_{i}.txt")
                print(f"writing {f}")
                f.write_text(doc.page_content)
        i = i + 1
    print("papers loading finished")

def with_papers_incremental(folder: Optional[Path] = None, skip_existing: bool = True):
    papers: list[Path] = traverse(folder, lambda p: "pdf" in p.suffix)
    print(f"indexing {len(papers)} papers")
    i = 1
    max = len(papers)
    for p in papers:
        loader = UnstructuredPDFLoader(str(p))
        print(f"adding paper {i} out of {max}")
        docs: list[Document] = loader.load()
        if len(docs) ==1:
            f = p.parent / f"{p.stem}.txt"
            print(f"writing {f}")
            f.write_text(docs[0].page_content)
        else:
            for i, doc in enumerate(docs):
                f = (p.parent / f"{p.stem}_{i}.txt")
                print(f"writing {f}")
                f.write_text(doc.page_content)
        i = i + 1
    print("papers loading finished")
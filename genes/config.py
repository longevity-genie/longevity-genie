from pathlib import Path
from pycomfort.files import *


class Locations:
    base: Path
    data: Path
    papers: Path

    def __init__(self, base: Path):
        self.base = base.absolute().resolve()
        self.data = self.base / "data"
        self.modules_data = self.data / "modules"
        self.paper_index = self.data / "index"
        assert self.data.exists(), "data subfolder should exist!"
        self.papers = self.data / "papers"
        assert self.papers.exists(), "papers subfolder should exist"
        self.modules = self.base / "modules"



from pathlib import Path
from pycomfort.files import *


class Locations:
    base: Path
    data: Path
    papers: Path
    oakvar: Path
    oakvar_modules: Path
    annotators: Path
    postaggregators: Path

    just_longevitymap: Path

    just_drugs: Path
    just_prs: Path
    just_coronary: Path
    just_cancer: Path
    just_lipidmetabolism: Path
    just_longevitymap: Path
    just_superhuman: Path
    just_cardio: Path
    just_thrombophilia: Path
    modules_text_data: Path

    longevity_map_text: Path
    cancer_text: Path
    lipidmetabolism_text: Path
    clinvar_text: Path

    clinpred_db: Path

    def annotator_data(self, name: str):
        return self.annotators / name / "data"

    def postaggregator_db(self, name: str, debug: bool = False):
        data = self.postaggregators / name / "data"
        if not data.exists():
            if debug:
                print(f"cannot find sqlite database {data}")
            return data
        dbs = with_ext(self.postaggregators / name / "data", "sqlite").to_list()
        if len(dbs) == 0:
            if debug:
                print(f"cannot find sqlite database {data}")
            return data
        else:
            return dbs[0]

    def __init__(self, base: Path, oakvar: Optional[str] = None):
        if oakvar is None:
            home_dir = Path.home()
            self.oakvar = home_dir / ".oakvar"
            if not self.oakvar.exists():
                print(f"{self.oakvar} does not exist!")
        else:
            self.oakvar = oakvar
        self.oakvar_modules = self.oakvar / "modules"
        self.annotators = self.oakvar_modules / "aggregators"
        self.postaggregators = self.oakvar_modules / "postaggregators"
        self.clinvar_data = self.annotator_data("clinvar")
        self.clinpred_data = self.annotator_data("clinvar")
        self.base = base.absolute().resolve()
        self.data = self.base / "data"
        self.modules_data = self.data / "modules"
        self.modules_text_data = self.modules_data / "texts"
        self.paper_index = self.data / "index"
        assert self.data.exists(), "data subfolder should exist!"
        self.papers = self.data / "papers"
        self.trials = self.data / "index" / "trials"
        self.dois = self.modules_data / "dois.tsv"
        assert self.papers.exists(), "papers subfolder should exist"
        self.modules = self.base / "modules"
        self.set_up_modules()
        self.set_up_outputs()

    def set_up_modules(self):
        self.clinvar = self.data / "clinvar" / "ncbi_clinvar_only.sqlite3"
        self.just_drugs = self.postaggregator_db("just_drugs")
        self.just_prs = self.postaggregator_db("just_prs")
        self.just_coronary = self.postaggregator_db("just_coronary")
        self.just_cancer = self.postaggregator_db("just_cancer")
        self.just_lipidmetabolism = self.postaggregator_db("just_lipidmetabolism")
        self.just_longevitymap = self.postaggregator_db("just_longevitymap")
        self.just_superhuman = self.postaggregator_db("just_superhuman")
        self.just_cardio = self.postaggregator_db("just_cardio")
        self.just_thrombophilia = self.postaggregator_db("just_thrombophilia")

    def set_up_outputs(self):
        self.clinvar_text = self.modules_text_data / "ncbi_clinvar_text.tsv"
        self.longevity_map_text = self.modules_text_data / "longevity_map_text.tsv"




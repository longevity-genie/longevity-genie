from pathlib import Path

from langchain.embeddings import OpenAIEmbeddings, LlamaCppEmbeddings, VertexAIEmbeddings
from langchain.embeddings.base import Embeddings
from pycomfort.files import *
import dotenv
from dotenv import load_dotenv
import os

def resolve_embeddings(embeddings_name: str) -> Embeddings:
    if embeddings_name == "openai":
        return OpenAIEmbeddings()
    elif embeddings_name == "lambda":
        return LlamaCppEmbeddings()
    elif embeddings_name == "vertexai":
        return VertexAIEmbeddings()
    else:
        print(f"{embeddings_name} is not yet supported by CLI, using default openai embeddings instead")
        return OpenAIEmbeddings()

def with_date_time(session: str, to_replace: str = "<datetime>") -> str:
    import datetime
    # Get the current date and time
    current_datetime = datetime.datetime.now()
    # Convert the datetime object to a string in the desired format
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    # Replace <datetime> with the formatted datetime string
    updated_string = session.replace(to_replace, formatted_datetime)
    # Print the updated string
    return updated_string


def start_tracing(session: str = "default", hosted: bool = True):
    session_name = with_date_time(session)
    os.environ["LANGCHAIN_SESSION"] = session_name
    print(f"start tracing into {session_name}")
    os.environ["LANGCHAIN_HANDLER"] = "langchain"
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    if hosted:
        os.environ["LANGCHAIN_ENDPOINT"] = "https://api.langchain.plus"
        #os.environ["LANGCHAIN_API_KEY"] = "<your-api-key>"

def load_environment_keys(debug: bool = True):
    e = dotenv.find_dotenv()
    if debug:
        print(f"environment found at {e}")
    has_env: bool = load_dotenv(e, verbose=True, override=True)
    if not has_env:
        print("Did not found environment file, using system OpenAI key (if exists)")
    openai_key = os.getenv('OPENAI_API_KEY')
    return openai_key


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
    coronary_text: Path

    clinpred_db: Path
    reports: Path
    report_anton: Path

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
        self.index = self.data / "index"
        assert self.data.exists(), "data subfolder should exist!"
        self.papers = self.data / "papers"
        self.trials = self.data / "index" / "trials"
        self.dois = self.modules_data / "dois.tsv"
        assert self.papers.exists(), "papers subfolder should exist"
        self.modules = self.base / "modules"
        self.reports = self.data / "reports"
        self.report_anton = self.reports / "report_Anton.tsv"
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
        self.clinvar_text = self.modules_text_data / "clinvar_text.tsv"
        self.longevity_map_text = self.modules_text_data / "longevity_map_text.tsv"
        self.coronary_text = self.modules_text_data / "coronary_text.tsv"




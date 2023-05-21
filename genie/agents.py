from langchain.llms.openai import OpenAI
from langchain.agents import create_csv_agent
from genie.config import Locations
from pathlib import Path


def init_csv_agent(verbose: bool = True, base: str = '.', trial_file_name: str = '.csv'):
    locations = Locations(Path(base))
    agent = create_csv_agent(OpenAI(temperature=0), locations.trials / trial_file_name, verbose=verbose)
    return agent

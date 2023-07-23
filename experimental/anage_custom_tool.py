# dependency on python-Levenshtein, thefuzz, polars
from dotenv import load_dotenv
_ = load_dotenv("test.env", override=True)

from langchain.agents import tool
from langchain.agents import AgentType, initialize_agent
from langchain.llms import OpenAI
import thefuzz.fuzz as fuzz
import polars as pl


llm = OpenAI(temperature=0)

@tool
def longevity(search_text: str) -> str:
    """Returns table with species latin names, common names and maximum age (longevity), use this for any \
    questions related to knowing animal or human maximum life span. \
    The input should always be creature name, (species name or common name), \
    and this function will always return its maximum life span, longevity in years.
    If there is no creature name in the table say its life span is unknown."""

    search_text = " "+search_text+" "
    def levenshtein_dist(struct: dict) -> int:
        return max(fuzz.partial_ratio(struct["Species"], search_text), fuzz.partial_ratio(struct["Common name"], search_text))

    frame = pl.read_csv("species_age.csv")
    frame = frame.with_columns((pl.col("Species") + " " + pl.col("Common name")).alias("name"))
    frame = frame.select([pl.struct(["Species", "Common name"]).apply(levenshtein_dist).alias("dist"), "Species", "Common name",
                          "Maximum longevity (yrs)"])
    frame = frame.sort(by="dist", reverse=True).select(["Species", "Common name", "Maximum longevity (yrs)"])

    return frame.head(8)

agent = initialize_agent(
    [longevity],
    llm,
    agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose = True)

print(agent.run("How long live arctic surfclam?"))


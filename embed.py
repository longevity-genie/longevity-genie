#!/usr/bin/env python3
import pprint

import click
from click.core import Context
from langchain.agents import AgentExecutor
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma

from genie.agents import init_csv_agent, init_simple_llm_agent
from genie.config import load_environment_keys, start_tracing


@click.group(invoke_without_command=True)
@click.pass_context
def app(ctx: Context):
    #if ctx.invoked_subcommand is None:
    #click.echo('Running the default command...')
    #test_index()
    pass

@app.command("test")
@click.option("--model", default="menadsa/S-BioELECTRA", help = "name of the model to test")
def test_command(model: str):
    # Get embeddings.
    embeddings = HuggingFaceEmbeddings(model_name=model)
    print(f"TESTING EMBEDDINGS FOR {model}")

    texts = [
        "Basquetball is a great sport.",
        "Fly me to the moon is one of my favourite songs.",
        "The Celtics are my favourite team.",
        "This is a document about the Boston Celtics",
        "I simply love going to the movies",
        "The Boston Celtics won the game by 20 points",
        "This is just a random text.",
        "Elden Ring is one of the best games in the last 15 years.",
        "L. Kornet is one of the best Celtics players.",
        "Larry Bird was an iconic NBA player.",
    ]

    # Create a retriever
    retriever = Chroma.from_texts(texts, embedding=embeddings).as_retriever(
        search_kwargs={"k": 10}
    )
    query = "What can you tell me about the Celtics?"

    # Get relevant documents ordered by relevance score
    docs = retriever.get_relevant_documents(query)
    print("NOW PRINTING RESULTS!")
    pprint.pprint(docs)
    return docs


if __name__ == '__main__':
    openai_key = load_environment_keys(debug=True)
    app()
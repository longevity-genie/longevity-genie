#!/usr/bin/env python3

import pprint

import click
from click.core import Context
from indexpaper.resolvers import *
from indexpaper.resolvers import Device
from langchain.agents import AgentExecutor
from langchain.chains import ConversationalRetrievalChain
from langchain.embeddings import OpenAIEmbeddings
from langchain.memory import ChatMessageHistory, ConversationBufferMemory
from langchain.vectorstores import Qdrant
from langchain.vectorstores.base import VectorStoreRetriever
from qdrant_client import QdrantClient

from genie.agents import init_csv_agent, init_simple_llm_agent
from genie.config import load_environment_keys, start_tracing


#from genie.indexing import Index


@click.group(invoke_without_command=True)
@click.pass_context
def app(ctx: Context):
    #if ctx.invoked_subcommand is None:
        #click.echo('Running the default command...')
        #test_index()
    pass



@app.command("failure_reasons")
@click.option('--verbose', default=True, help='whether you want to see all thoughts of the model')
@click.option('--base', default='.', help='start folder for Locations object')
@click.option('--trial_file_name', default='ct_denorm_dataset.csv', help='name of the csv file')
@click.option('--num', default=1, help='number of the result')
@click.option("--session", default="get_trials_reasons", help = "session on langchain")
@click.option("--hosted", default=True, help = "if traced session is hosted")
def get_trials_reasons(verbose: bool, base: str, trial_file_name: str, num: int, session: str, hosted: bool):
    start_tracing(session, hosted)
    csv_agent: AgentExecutor = init_csv_agent(verbose, base, trial_file_name)
    question =f"""
    Perform the following actions:
    1 - Get clinical trials that study```cancer``` condition, case insensitive.
    2 - From that take only those that have started not earlier than last 5 years from 2023-05-21 including.
    3 - From that take only those trials that involve drug interventions
    4 - Create new column "is_successful" and fill it with boolean values. Column should have true values for successful trials and false for unsuccessful
    5 - Take only rows where "is_successful" is False
    6 - Find id of the trial number  {num} in the dataset from the previous step
    7 - Print id from the previous step
    8 - Parse text of the response from this web page https://clinicaltrials.gov/ct2/show/```id```.
    9 - Remove tags, styles and scripts, than remove new lines and get only text.
    """
    llm_agent = init_simple_llm_agent()
    res = csv_agent.run(question)
    result = llm_agent(question + res)
    print(f"RESULTS: \n {result}")



"""
@app.command("test")
@click.option('--chain', default="stuff", type=click.Choice(["stuff", "map_reduce", "refine", "map_rerank"], case_sensitive=True), help="chain type")
#@click.option('--model', default="gpt-4")
@click.option('--model', default="gpt-3.5-turbo")
@click.option('--search', default='similarity', type=click.Choice(["similarity", "mmr"], case_sensitive=True), help='search type')
@click.option('--k', default = 0, help = "search kwargs")
@click.option('--base', default='.', help='base folder')
@click.option("--session", default="text_index", help = "session on langchain")
@click.option("--hosted", default=True, help = "if traced session is hosted")
def test_index(chain: str,  model: str, search: str, k: int,  base: str, session: str = "text_index", hosted: bool = True):
    locations = Locations(Path(base))
    start_tracing(session, hosted=hosted)
    index = Index(locations.index, model, chain_type=chain, search_type=search, k = k) #Index(locations, "gpt-4")
    #question1 = f"There are rs4946936, rs2802290, rs9400239, rs7762395, rs13217795 genetic variants in FOXO gene, explain their connection with aging and longevity"
    #question1 = f"There are rs4946936, rs2802290, rs9400239, rs7762395, rs13217795 genetic polymorphisms, for each of them explain what this genetic variant is about, its association with longevity, aging and diseases, also explain the role of the gene it belongs to."
    #question1= f"There are rs1800392 rs3024239 rs2072454 rs3842755 genetic polymorphisms, for each of them explain what this genetic variant is about, its association with longevity, aging and diseases, also explain the role of the gene it belongs to."
    question1 = "There are rs4946936, rs2802290, rs9400239, rs7762395, rs13217795 genetic polymorphisms in the FOXO gene, explain their connection with aging and longevity"
    print(f"Q1: {question1}")
    answer1 = index.query_with_sources(question1, [])
    print(f"A1: {answer1}")
"""





@app.command("test")
@click.option('--question', default="How long can gray whale live?", help = "question to ask LLM")
@click.option('--collection_name', default="bge_large_512_moskalev_papers_paragraphs", help = "question to ask LLM")
@click.option('--embedding_model', default="BAAI/bge-large-en", help = "which embedding model to use")
def test(question: str, collection_name: str, embedding_model: str):

    from langchain.chat_models import ChatOpenAI

    load_environment_keys()

    url = "https://5bea7502-97d4-4876-98af-0cdf8af4bd18.us-east-1-0.aws.cloud.qdrant.io:6333" if os.getenv("db") is None else os.getenv("db")
    client: QdrantClient = QdrantClient(
        url=url,
        port=6333,
        grpc_port=6334,
        prefer_grpc=True,
        api_key=os.getenv("QDRANT_KEY")
    )
    collections = [c.name for c in client.get_collections().collections]
    print(f"COLLECTIONS ARE: {collections} \n")

    device = Device.cpu
    #embedding_model = "BAAI/bge-base-en" #EmbeddingModels.bge_base_en
    #collection_name = 'biolinkbert_512_moskalev_papers'
    #collection_name = 'bge_base_512_moskalev_papers_paragraphs_10'

    if "ada2" in collection_name or "ada-" in collection_name:
        embeddings = OpenAIEmbeddings()
    elif "bge" in collection_name:
        embeddings = resolve_embeddings(EmbeddingType.HuggingFaceBGE, model=embedding_model)
    else:
        embeddings = resolve_embeddings(EmbeddingType.HuggingFace, model=embedding_model, device=device)
        pprint.pprint(embeddings)
        print(collection_name)
    default_model = "gpt-3.5-turbo-16k"
    llm = ChatOpenAI(model = default_model)

    db = Qdrant(client, collection_name=collection_name, embeddings=embeddings)
    retriever: VectorStoreRetriever = db.as_retriever()
    verbose: bool = True


    memory = ConversationBufferMemory(memory_key="chat_history")
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        verbose=verbose, memory = memory
    )

    #result = chain.invoke({"question": question, "chat_history": []})
    return chain, memory



if __name__ == '__main__':
    openai_key = load_environment_keys(debug=True)
    #print(f"The key is {openai_key}")
    app()
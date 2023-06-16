#!/usr/bin/env python3

import os
import click
import dotenv

from click import Context
from dotenv import load_dotenv

from genie.config import Locations,load_environment_keys
from genie.calls import longevity_gpt
from genie.indexing import *
openai_key = load_environment_keys()

@click.group(invoke_without_command=False)
@click.pass_context
def app(ctx: Context):
    #if ctx.invoked_subcommand is None:
    #    click.echo('Running the default command...')
    #    test_index()
    pass

@app.command("write")
@click.option('--model', default='gpt-3.5-turbo-16k', help='model to use, gpt-3.5-turbo-16k by default')
@click.option('--proofread', default=True, help='if we prefer proofread papers')
@click.option('--base', default='.', help='base folder')
def write(model: str, proofread: bool, base: str):
    load_dotenv()
    locations = Locations(Path(base))
    index = Index(locations.index, model)
    print("saving modules and papers")
    index.with_modules(locations.modules_text_data).with_papers(locations.papers, proofread=proofread).persist()

@app.command("clinvar")
@click.option('--model', default='gpt-3.5-turbo-16k', help='model to use, gpt-3.5-turbo-16k by default')
@click.option('--base', default='.', help='base folder')
def index_clinvar(model: str, base: str):
    load_dotenv()
    locations = Locations(Path(base))
    output = locations.clinvar_text
    prepare_clinvar(locations.clinvar, output)
    index = Index(locations.index, model)
    print("saving modules and papers")
    index.with_modules(output).persist()

@app.command("longevity_gpt")
@click.option('--question', default='What is aging?', help='Question to be asked')
def longevity_gpt_command(question: str):
    return longevity_gpt(question, []) # TODO rewrite as agent


@app.command("test")
@click.option('--chain', default="map_reduce", type=click.Choice(["stuff", "map_reduce", "refine", "map_rerank"], case_sensitive=True), help="chain type")
#@click.option('--process', default="split", help="preprocessing type")
@click.option('--model', default="gpt-3.5-turbo-16k")
@click.option('--search', default='similarity', type=click.Choice(["similarity", "mmr"], case_sensitive=True), help='search type')
@click.option('--k', default = 0, help = "search kwargs")
@click.option('--base', default='.', help='base folder')
def test_index(chain: str,  model: str, search: str, k: int,  base: str):
    locations = Locations(Path(base))
    index = Index(locations.index, model, chain_type=chain, search_type=search, k = k) #Index(locations, "gpt-4")
    #question1 = f"There are rs4946936, rs2802290, rs9400239, rs7762395, rs13217795 genetic variants in FOXO gene, explain their connection with aging and longevity"
    #question1 = f"There are rs4946936, rs2802290, rs9400239, rs7762395, rs13217795 genetic polymorphisms, for each of them explain what this genetic variant is about, its association with longevity, aging and diseases, also explain the role of the gene it belongs to."
    #question1= f"There are rs1800392 rs3024239 rs2072454 rs3842755 genetic polymorphisms, for each of them explain what this genetic variant is about, its association with longevity, aging and diseases, also explain the role of the gene it belongs to."
    question1 = "There are rs4946936, rs2802290, rs9400239, rs7762395, rs13217795 genetic polymorphisms in the FOXO gene, explain their connection with aging and longevity"
    print(f"Q1: {question1}")
    answer1 = index.query_with_sources(question1, [])
    print(f"A1: {answer1}")

#prompt=PromptTemplate.from_template('tell us a joke about {topic}')
if __name__ == '__main__':
    app()
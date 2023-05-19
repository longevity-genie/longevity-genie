import os

import click
import dotenv
from click import Context
from dotenv import load_dotenv

from genie.indexing import *

e = dotenv.find_dotenv()
print(f"environment found at {e}")
has_env: bool = load_dotenv(e, verbose=True)
if not has_env:
    print("Did not found environment file, using system OpenAI key (if exists)")
openai_key = os.getenv('OPENAI_API_KEY')
#print(f"OPENAI key is {openai_key}")

@click.group(invoke_without_command=False)
@click.pass_context
def app(ctx: Context):
    #if ctx.invoked_subcommand is None:
    #    click.echo('Running the default command...')
    #    test_index()
    pass

@app.command("write")
@click.option('--model', default='gpt-3.5-turbo', help='model to use, gpt-3.5-turbo by default')
@click.option('--base', default='.', help='base folder')
def write(model: str, base: str):
    load_dotenv()
    locations = Locations(Path(base))
    index = Index(locations, model)
    print("saving modules and papers")
    index.with_modules().with_papers().persist()


@app.command("test")
@click.option('--base', default='.', help='base folder')
def test_index(base: str):
    locations = Locations(Path(base))
    index = Index(locations, "gpt-3.5-turbo") #Index(locations, "gpt-4")
    #index.with_modules()
    question1 = f"There are rs4946936, rs2802290, rs9400239, rs7762395, rs13217795 in FOXO gene, explain their connection with aging and longevity"
    print(f"Q1: {question1}")
    answer1 = index.query_with_sources(question1)
    print(f"A1: {answer1}")

if __name__ == '__main__':
    app()
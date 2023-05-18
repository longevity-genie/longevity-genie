import click
from dotenv import load_dotenv

from genie.indexing import *


@click.group(invoke_without_command=True)
@click.pass_context
def app(ctx):
    if ctx.invoked_subcommand is None:
        click.echo('Running the default command...')
        #test_index()

@app.command("write")
@click.option('--model', default='gpt-4', help='model to use, gpt-4 by default')
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
    load_dotenv()
    locations = Locations(Path(base))
    index = Index(locations, "gpt-4") #Index(locations, "gpt-4")
    #index.with_modules()
    question1 = f"There are rs4946936, rs2802290, rs9400239, rs7762395, rs13217795 in FOXO gene, explain their connection with aging and longevity"
    print(f"Q1: {question1}")
    answer1 = index.query_with_sources(question1)
    print(f"A1: {answer1}")

if __name__ == '__main__':
    app()
import click
from click.core import Context
from langchain.agents import AgentExecutor

from genie.constants import prompt_1, prompt_2, prompt_3, prompt_4, prompt_5, prompt_6
from genie.agents import init_csv_agent, init_simple_llm_agent


@click.group(invoke_without_command=True)
@click.pass_context
def app(ctx: Context):
    if ctx.invoked_subcommand is None:
        click.echo('Running the default command...')
        calculate_trials_statistics()


def calculate_trials_statistics(verbose: bool = True, base: str = ".", trial_file_name: str = 'ct_denorm_dataset.csv', prompt_number: str = "4"):
    agent = init_csv_agent(verbose, base, trial_file_name)
    prompts_dict = {
        '1': prompt_1,
        '2': prompt_2,
        '3': prompt_3,
        '4': prompt_4
    }
    print('Calculating statistics for the file {0}'.format(trial_file_name))
    print(prompts_dict[prompt_number])
    return agent.run(prompts_dict[prompt_number])

@app.command("calculate_trials_statistics")
@click.option('--verbose', default=True, help='whether you want to see all thoughts of the model')
@click.option('--base', default='.', help='start folder for Locations object')
@click.option('--trial_file_name', default='ct_denorm_dataset.csv', help='name of the csv file')
@click.option('--prompt_number', default='1', help='the id of prompt you want to try')
def calculate_trials_statistics_command(verbose: bool, base: str, trial_file_name: str, prompt_number: str):
    return calculate_trials_statistics(verbose, base, trial_file_name, prompt_number)


def get_trials_reasons(verbose: bool = True, base: str = ".", trial_file_name: str = 'ct_denorm_dataset.csv') -> str:
    csv_agent: AgentExecutor = init_csv_agent(verbose, base, trial_file_name)
    llm_agent = init_simple_llm_agent()
    res = csv_agent.run(prompt_5)
    result = llm_agent(prompt_6 + res)
    return result


@app.command("get_trials_reasons")
@click.option('--verbose', default=True, help='whether you want to see all thoughts of the model')
@click.option('--base', default='.', help='start folder for Locations object')
@click.option('--trial_file_name', default='ct_denorm_dataset.csv', help='name of the csv file')
def get_trials_reasons_command(verbose: bool = True, base: str = ".", trial_file_name: str = 'ct_denorm_dataset.csv') -> str:
    return get_trials_reasons(verbose, base, trial_file_name)


if __name__ == '__main__':
    app()

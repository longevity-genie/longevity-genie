# longevity-genie
A model that should answer questions about genes and variants

# setting things up

## Git clone the repository:
```bash
git@github.com:dna-seq/longevity-genie.git
```
Set up the environment. You can use micromamba, conda or anaconda to do this, with exception of executable all commands are the same in all cases.
We are usually using [micromamba](https://mamba.readthedocs.io/en/latest/user_guide/micromamba.html) as it is the fastest
```
micromamba create -f environment.yaml
micromamba activate longevity-genie
```
## Pull data from DVC
We are using [DVC](http://dvc.org) for data version control. 
It is required because database index does not fit into git.
To set it up do:
```bash
dvc pull
```
We use Google Drive to store data so it may ask you to authorize data access.

# Existing scripts

Here are some additional scripts you may be interested in running.
We store the index in DVC so you do not need to run them to set things up.

### download.py ###

Downloads papers
```
python download.py download_papers
```

### index.py ###

Makes chroma index out of parsed papers:
```bash
python index.py write
```
The index is written to /data/index as parquet files. You can then do:
```bash
dvc commit
dvc push
```
to push changed to google drive associated with the index data.

To test the index with a test query
```
python index.py test
```

### agent.py ###

To test the CSV agent with prompts (currently for trials statistics)
CSV is stored in /index/trials folder
```
python agent.py calculate_trials_statistics --prompt_number=1
```

### chat.py ###

To run webinterface of the chat (temporally broken, because weavite integration did not work well):
```
python chat.py
```
### rest.py ### 
To run rest-api for the telegram chat-bot:
```
python rest.py
```
Telegram chat-bot is situated at https://github.com/dna-seq/longevitygpt_telegram_bot

Lang-chain tracing
==================

For langchain tracing you need to enable langchain server with docker compose:
```bash
sudo docker compose -f tracing.yaml up
```
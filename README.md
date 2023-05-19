# longevity-genie
A model that should answer questions about genes and variants

# setting things up
## Environment
Use micromamba to activate the environment

```
micromamba create -f environment.yaml
micromamba activate longevity-genie
```

## Indexing genetic data

In Locations we have some oakvar-specific paths, but so far it is optional.

## Running the files

There are multiple scripts in the root of the folder.

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
The index is written to /data/index as parquet files

To test the index with a test query
```
python index.py test
```

### chat.py ###

To run webinterface of the chat (temporaly broken, because weavite integration did not work well):
```
python chat.py
```
### rest.py ### 
To run rest-api for the telegram chat-bot:
```
python rest.py
```
Telegram chat-bot is situated at https://github.com/dna-seq/longevitygpt_telegram_bot
# longevity-genie
A model that should answer questions about genes and variants

# setting things up
## Environment
Use micromamba to activate the environment

```
micromamba create -f environment.yaml
micromamba activate genes-gpt
```

## Initializing submodules

We take list of samples from submodules, please initialize them before running anything else:
```
git submodule update --init --recursive
```
## Running the files
To download papers use download.py scripts:
```
python download.py download_papers
```
To make chroma index out of them:
```
python download.py index
```

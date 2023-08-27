# longevity-genie

The core idea about Longevity genie project is extending abilities of large language models (LLMs) to answer questions about personal health, genetics and longevity research.
Currently, LLMs like ChatGPT (and also numerous LLAMA/ALPACA based opensource models) do not possess domain-specific biological knowledge and often hallucinate (make things up) when you ask it specific question.
There are different ways to improve it:
* extending user prompts with additional instructions on how the model should behave
* using vector similarity search in vector databases that will extend that user prompts with additional results
* using LLM-driven agents that will use search, code writing, SQL and other tools to extract information from external sources when answering user request
* using LLM-driven routing when the query is routed to different subchains and agents depending on its content
* fine-tuning of existing models to work better with new data - such approach will be possible if we will switch from GPT4 to smallerr opensource models that can be fine-tined with QLora and similar techniques.

We are actively applying langchain to build the system. If you have not used it before [this course](https://learn.deeplearning.ai/langchain) is very good to get started.

# DISCLAIMER

The project is in active refactoring, so part of the features is temorally broken.

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

# Environment

To run openai API and langchain tracing you need keys in your environment variables. 
Do not forget to put on your openai and langchain trace keys.
In .env.template there are environment variables, fill them in with your keys and rename to .env.


### index.py ###

To run webinterface of the chat (temporally broken, because weavite integration did not work well):
```
python index.py
```

# Setting up database #

To make things work you have to setup qdrant database or connect to the existing one
We provide https://huggingface.co/datasets/longevity-genie/bge_large_512_aging_papers_paragraphs and https://huggingface.co/datasets/longevity-genie/biolinkbert_large_512_aging_papers_paragraphs
Datasets that you can upload as snapshots of the collections in your qdrant database.

To set up the local one go to services folder and then:
```
cd services
docker compose up -d
```
If everything went right you will be able to see: http://localhost:6333/dashboard
In the dashboard you can upload our snapshots of the papers collections: https://huggingface.co/datasets/longevity-genie/bge_large_512_aging_papers_paragraphs and https://huggingface.co/datasets/longevity-genie/biolinkbert_large_512_aging_papers_paragraphs
Then make sure you specify all keys and DATABASE_URL in your .env file. For the easy of use we provide a .env.template
If you run QDRANT database locally you do not need to fill its key.

# Gratitude

The project was a hackathon idea at Zuzalu.
Big thanks to:

* @nikhilYadala for help with LongevityGPT integration and help with GPT4 key
* Zuzalu organizers for making the place where idea incubated happen
* Vita DAO for supporting the project

![great thanks to vitadao](https://avatars.githubusercontent.com/u/84313344?s=200&v=4)

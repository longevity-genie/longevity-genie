from enum import Enum

token_limits = {
    "gpt-4-32k": 32768,
    "gpt-4": 8192,
    "gpt-3.5-turbo-16k": 16384,
    "gpt-3.5-turbo": 4096,
    "other": 4096
}


class ChainType(Enum):
    Stuff = "stuff"
    MapReduce = "map_reduce"
    Refine = "refine"
    MapRerank = "map_rerank"


class SearchType(Enum):
    similarity = "similarity"
    mmr = "mmr"
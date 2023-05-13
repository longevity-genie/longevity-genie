from pathlib import Path
from typing import Optional

import polars as pl
from pynction import Try

from genes.sqlite import get_query_df
from genes.config import Locations
from functional import seq
from genes.downloads import try_doi_from_pubmed

def prepare_longevity_doi(locations: Locations, keep_not_found: bool = True, pubmed_name: str = "quickpubmed") -> pl.DataFrame:
    where = locations.dois
    doi_col: pl.Expr = pl.col(pubmed_name).apply(lambda p: try_doi_from_pubmed(p).get_or_else_get(lambda v: p if keep_not_found else "")).alias("doi")
    pubmeds = get_query_df(locations.just_longevitymap, "SELECT DISTINCT quickpubmed from variant").select(pl.col(pubmed_name), doi_col)
    if where.exists():
        prev = pl.read_csv(where, sep="\t")
        joined = pl.concat(pubmeds, prev).unique()
        joined.write_csv(where, sep="\t")
        return joined
    else:
        pubmeds.write_csv(where, sep="\t")
    print(f"writing {pubmeds.shape[0]} dois to {where}")
    return pubmeds

def prepare_longevity(locations: Locations):
    query = """
SELECT identifier, study_design, conclusions, association, gender, quickpubmed, location, population.name as population_name , quickyear, gene.name as gene_name, gene.symbol as gene_symbol,  gene.description
FROM variant, gene, population
WHERE gene.id == variant.gene_id AND population.id == variant.id
"""
    dois = pl.read_csv(locations.dois, sep="\t").with_columns([pl.col("quickpubmed").cast(pl.Utf8)])
    df = get_query_df(locations.just_longevitymap, query).join(dois, on="quickpubmed")
    id_col = (pl.col("identifier")  +pl.lit("_in_")+pl.col("doi")).alias("id")
    source = (pl.lit("http://doi.org/") + pl.col("doi")).alias("source")
    text_col: pl.Expr = (
            pl.col("identifier") + pl.lit(" variant in  ") + pl.col("gene_name") + pl.lit(" (") + pl.col("gene_symbol") + pl.lit(") ")
            + pl.lit("with location ") +
            pl.col("location") + pl.lit(" has ") +
            pl.col("association") +
            pl.lit(" association with longevity for ") + pl.col("gender").str.replace("/", " and ") +
            pl.lit("in ") + pl.col("population_name") + pl.lit(" population") +
            pl.lit("in a study conducted/published in ") + pl.col("quickyear").cast(pl.Utf8) +
            pl.lit(". The study had the following design ") + pl.col("study_design") + pl.lit(". The study concluded") + pl.col("conclusions")
            + pl.lit("The study was published with pubmed id") +
            pl.col("quickpubmed").cast(pl.Utf8) + pl.lit(" with DOI ") + source
    ).alias("text")
    for_index = df.select([id_col,
                           pl.col("identifier"),
                           pl.col("gene_symbol"),
                           pl.col("population_name").alias("population"),
                           pl.col("gender"),
                           pl.col("quickpubmed").cast(pl.Utf8).alias("pubmed"),
                           pl.col("doi"),
                           source,
                           text_col])
    for_index.write_csv(locations.longevity_map_text, sep="\t")
    print("written to locations.longevity_map_text")
    return for_index
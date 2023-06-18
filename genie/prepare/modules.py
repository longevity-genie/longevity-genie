from pathlib import Path
from typing import List

import polars as pl
from chromadb.api.types import Document
from functional import seq
from langchain.document_loaders import DataFrameLoader
from pycomfort.files import with_ext

from genie.config import Locations
from genie.prepare.downloads import try_doi_from_pubmed
from genie.sqlite import get_query_df
import pandas as pd

#TODO: get rid of locations

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

def prepare_longevity(just_longevitymap: Path, dois: Path):
    """
    :param just_longevity_map: where we have sql for longevity map
    :param dois: where doi resolution table is
    :param longevity_map_text: where to write the text dataframe output
    :return:
    """
    query = """
SELECT identifier, study_design, conclusions, association, gender, quickpubmed, location, population.name as population_name , quickyear, gene.name as gene_name, gene.symbol as gene_symbol,  gene.description
FROM variant, gene, population
WHERE gene.id == variant.gene_id AND population.id == variant.id
"""
    dois = pl.read_csv(dois, sep="\t").with_columns([pl.col("quickpubmed").cast(pl.Utf8)])
    df = get_query_df(just_longevitymap, query).join(dois, on="quickpubmed")
    id_col = (pl.col("identifier")  +pl.lit("_in_")+pl.col("doi")).alias("id")
    source = (pl.lit("http://doi.org/") + pl.col("doi")).alias("source")
    text_col: pl.Expr = (
            pl.col("identifier") + pl.lit(" genetic variant in  ") + pl.col("gene_name") + pl.lit(" (") + pl.col("gene_symbol") + pl.lit(") ")
            + pl.lit("with location ") +
            pl.col("location") + pl.lit(" has ") +
            pl.col("association") +
            pl.lit(" association with longevity for ") + pl.col("gender").str.replace("/", " and ") +
            pl.lit("in ") + pl.col("population_name") + pl.lit(" population") +
            pl.lit(" in a study conducted in ") + pl.col("quickyear").cast(pl.Utf8) +
            pl.lit(". The study had the following design: ") + pl.col("study_design") + pl.lit(". The study concluded the following. ") + pl.col("conclusions")
            + pl.lit("The study was published with pubmed id ") +
            pl.col("quickpubmed").cast(pl.Utf8) + pl.lit(" with DOI ") + source
    ).alias("text").str.replace("..", ".")
    return df.select([id_col,
                           pl.col("identifier"),
                           pl.col("gene_symbol"),
                           pl.col("population_name").alias("population"),
                           pl.col("gender"),
                           pl.col("quickpubmed").cast(pl.Utf8).alias("pubmed"),
                           pl.col("doi"),
                           source,
                           pl.col("association"),
                           text_col])

def prepare_coronary(just_coronary: Path):
    query= "SELECT * FROM coronary_disease;"
    df = get_query_df(just_coronary, query)
    df_updated = df.with_columns(
        [pl.col("PMID")
         .str.replace_all("PMID ", "https://www.ncbi.nlm.nih.gov/snp/")
         .str.replace_all("PMID: ", "https://www.ncbi.nlm.nih.gov/snp/")
         .str.replace_all(";", "")
         .alias("pmid_source"),
         pl.col("GWAS_study_design")
         .str.extract_all(r'\[([^]]+)\]')
         .arr.join("")
         .str.replace_all('\[PMID ', "https://www.ncbi.nlm.nih.gov/snp/")
         .str.replace_all('\[PMID: ', "https://www.ncbi.nlm.nih.gov/snp/")
         .str.replace_all('\]', " ")
         .alias("gwas_source")
         ]
    )
    text_col: pl.Expr = (
            pl.col("rsID") + pl.lit(" in gene ") + pl.col("Gene") +
            pl.lit(" with ") + pl.col("Genotype") + pl.lit("genotype ") +
            pl.lit("in ") + pl.col("Population") + pl.lit(" population") +
            pl.lit("with the following design ") + pl.col("GWAS_study_design") +
            pl.lit(". The study concluded:") + pl.col("Conclusion")
            + pl.lit("Links for mentioned studies: ") + pl.col("gwas_source") +
            pl.lit(". Other related articles: ") + pl.col("pmid_source")
    ).alias("text")
    return df_updated.select([
        pl.col("rsID"),
        pl.col("Gene"),
        pl.col("Genotype"),
        pl.col("Population"),
        pl.col("PMID").cast(pl.Utf8),
        pl.col("pmid_source"),
        pl.col("gwas_source"),
        text_col
    ])
def prepare_clinvar(clinvar_path: Path):
    query= "SELECT * FROM ncbi_clinvar;"
    df = get_query_df(clinvar_path, query)
    source = (pl.lit("https://www.ncbi.nlm.nih.gov/clinvar/variation/") + pl.col("clinvar_id").cast(pl.Utf8)).alias("source")
    text_col: pl.Expr = (
            pl.col("rsid").cast(pl.Utf8) + pl.lit(" is located in ") +  pl.col("chrom").cast(pl.Utf8) +
            pl.lit(" chromosome with position ")  + pl.col("pos").cast(pl.Utf8) +
            pl.lit(" which is in the gene ") + pl.col("symbol") +
            pl.lit(". This gene has the following description: ")+ pl.col("gene_description") +
            pl.lit(" This SNP can be associated with ") +pl.col("disease_names")+
            pl.lit(". Those associations have ") + pl.col("sig") + pl.lit(" clinical significance") +
            pl.lit(" and have review status: ") + pl.col("rev_stat") +
            pl.lit(". ") + pl.col("rsid").cast(pl.Utf8) + pl.lit("has the following disease references: ") +
            pl.col("disease_refs") +
            pl.lit(". Source: ") + source
    ).alias("text")
    return df.select([
        pl.col("rsid"),
        pl.col("chrom"),
        pl.col("pos"),
        pl.col("symbol"),
        pl.col("gene_description"),
        pl.col("disease_names"),
        pl.col("rev_stat"),
        pl.col("sig"),
        pl.col("clinvar_id").cast(pl.Utf8),
        source,
        text_col])

def tsv_to_documents(folder: Path)-> List[Document]:
    modules = with_ext(folder, "tsv").to_list() if folder.is_dir() else seq([folder])
    print(f"detected text for the following modules {modules}")
    modules_loaders = [DataFrameLoader(pd.read_csv(tsv, sep="\t")) for tsv in modules]
    print(f"indexing {len(modules_loaders)} modules")
    modules_docs: List[Document] = seq([loader.load() for loader in modules_loaders]).flatten().to_list()
    return modules_docs


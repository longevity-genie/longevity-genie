# useful utility methods grouped together
import polars as pl
from typing import Union, List
from pathlib import Path
from typing import Optional

def limit_resource(gbs: int = 30):
    import resource
    # Convert GB to bytes
    limit = gbs * 1024 * 1024 * 1024
    # Set the memory limit
    resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
    return limit

def with_struct_fields(df: pl.DataFrame, col: str, fields: Union[List[str], str], prefix: str = ""):
    """

    :param df:
    :param col:
    :param fields:
    :param prefix:
    :return:
    """
    fields = [fields] if isinstance(fields, str) else fields
    return df.with_columns([pl.col(col).struct.field(f).alias(prefix+f) for f in fields])


def write_s2orc(what: Path, n_rows: Optional[int] = None, output_folder: Optional[Path] = None) -> Path:
    df = pl.scan_ndjson(what, infer_schema_length=1000, n_rows=n_rows, low_memory=True)
    df_with_pubmed = with_struct_fields(df, "externalids", ["pubmed", "doi"]).filter(pl.col("pubmed").is_not_null())
    result = with_struct_fields(df_with_pubmed, "content", ["text"])
    name = what.stem + ".parquet"
    where = what.parent / name if output_folder is None else output_folder / name
    result.collect(streaming=True).write_parquet(where, use_pyarrow=True,compression_level=22, compression="zstd")
    return where

def filter_relevant(papers_df: pl.LazyFrame, key_word):
    return papers_df.filter(pl.col("text").str.contains("")).collect(streaming=True)



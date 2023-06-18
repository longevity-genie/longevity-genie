from pathlib import Path
import polars as pl

def prepare_longevity_map_qa(longevity_map_text_path: Path, qa: Path, upload_to_langchain_plus: bool = True):
    """
    Prepares question/answer datasets for langchain evaluation purposes
    :param longevity_map_text_path:
    :param qa: QA output path
    :param upload_to_langchain_plus: if we want to upload to langchain plus
    :return:
    """
    from langchainplus_sdk import LangChainPlusClient
    longevity_map_text = pl.read_csv(longevity_map_text_path, sep="\t")
    question = (pl.lit("How is ") +pl.col("identifier") + pl.lit(" connected with longevity?")).alias("question")
    answer = (pl.lit("Here is what we know about ") +
              pl.col("identifier") +
              pl.lit(" associations with longevity. ") +
              pl.col("text")
              ).alias("answer")
    longevity_map_qa = longevity_map_text.select([pl.col("identifier"), pl.col("text")]).groupby(pl.col("identifier")) \
        .agg(pl.col("text")) \
        .with_columns([
        pl.col("text").apply(lambda series: ' '.join(series))
    ]).select([question, answer])
    where = qa / "longevity_map_qa.tsv"
    longevity_map_qa.write_csv(where, sep="\t")
    if upload_to_langchain_plus:
        client = LangChainPlusClient()
        longevity_map_qa_pd = longevity_map_qa.to_pandas()
        client.delete_dataset(dataset_name="longevity_map_genetic_variants")
        client.upload_dataframe(longevity_map_qa_pd ,
                                name="longevity_map_genetic_variants",
                                description="This dataset is to evaluate if we can retrieve associations of longevity genetic variants",
                                input_keys=["question"],
                                output_keys=["answer"])
    return where

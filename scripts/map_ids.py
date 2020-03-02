import argparse
import requests

import lxml.etree as ET
import pandas as pd
import tqdm

def read_tag_chunks(id_file, batch_size):
    """ 
    Chunk the pandas dataframe so not everything is read into memory

    Keyword Arguments:
    id_file -- the file to read through pandas
    batch_size -- the size of each chunk
    """
    for pmids_df in pd.read_csv(id_file, chunksize=batch_size, sep="\t"):
        yield (
            pmids_df
            .drop_duplicates('pubmed_id')
            .rename(index=str, columns={"pubmed_id":"PMID"})
            .astype({"PMID":str})
        )

def map_ids(ids_file, id_output, debug):
    """
    Extracts pmids from pubtator and then attempts to map pmids to pmcids
    This section is subject to be blocked since it relies on api calls.
    If this script continues to be blocked please email the researchers at pubtator

    Outputs a TSV file with the following header terms:
    pubmed_id - the corresponding pubmed id
    pmcids - the corresponding pubmed central ids

    Keywords arguments:
    ids_file -- The path to the extracted tag file
    email -- email to be reached at
    id_batch -- the id batch to query pubmed central from
    id_output --- the file name for the mapped ids
    """
    if debug:
        pmids_to_pmcids = pd.read_csv(
            "data/example/ncbi_pmid_to_pmcid_map.tsv.xz", 
            dtype={
                "PMID": str,
                "Year": int,
                "Issue":str
            },
            sep="\t"
        )
    else:
        pmids_to_pmcids = pd.read_csv(
            "ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/PMC-ids.csv.gz", 
            dtype={
                "PMID": str,
                "Year": int,
                "Issue":str
            }
        )

    pmcid_batch = []
    for pmids_df in tqdm.tqdm(read_tag_chunks(ids_file, 1e6)):
        mapped_ids = pmids_to_pmcids.merge(pmids_df[["PMID"]], on="PMID")

        if not mapped_ids.empty:
            pmcid_batch.append(mapped_ids)


    full_mapped_ids = pd.concat(pmcid_batch)
    (
        full_mapped_ids
        .drop_duplicates()
        .to_csv(f"{id_output}", sep="\t", index=False)
    )

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extracts the annotations from the BioC xml format')
    parser.add_argument("--input", help="a tsv file that contains pmids to merge with pmcids list", required=True)
    parser.add_argument("--output", help="the name of the output file that contains mapped ids", default="pmids_to_pmcids_map.tsv")
    parser.add_argument("--debug", help="this flag is used to pre-load ncbi's pmid to pmcid id table", action="store_true")
    args = parser.parse_args()

    map_ids(args.input, args.output, args.debug)

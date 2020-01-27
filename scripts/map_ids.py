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
		yield pmids_df.drop_duplicates('pubmed_id')

def map_ids(ids_file, email, id_batch, id_output):
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
	pmids_to_pmcids = f"https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?tool=pubtator_parser&email={email}&ids="

	data_records = []
	for pmids_df in tqdm.tqdm(read_tag_chunks(ids_file, id_batch)):
		ids = f"{','.join(map(str, pmids_df.pubmed_id.values))}"
		response = requests.get(f"{pmids_to_pmcids}{ids}")
		
		if response.status_code != 200:
			raise Exception(response.text)

		id_root = ET.fromstring(response.text)
		id_records = map(
			lambda x: (x.attrib['pmid'], x.attrib['pmcid']), 
			filter(lambda x: "pmcid" in x.attrib, id_root.xpath("//record"))
		)
		
		data_records += [
			{"pmid":ids[0], "pmcids":ids[1]}
			for ids in id_records
		]

	pmcids_df = pd.DataFrame.from_records(data_records)
	pmcids_df.to_csv(f"{id_output}", sep="\t", index=False)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Extracts the annotations from the BioC xml format')
	parser.add_argument("--input", help="a tsv file that contains pmids to query for full text", required=True)
	parser.add_argument("--email", help="the email address to idenfity yourself", required=True)
	parser.add_argument("--id_batch", help="the number of ids to query at once", default=100, type=int)
	parser.add_argument("--output", help="the name of the output file that contains mapped ids", default="pmids_to_pmcids_map")
	args = parser.parse_args()

	map_ids(args.input, args.email, args.id_batch, args.output)
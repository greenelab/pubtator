import argparse
import requests

import lxml.etree as ET
import pandas as pd
import tqdm


def read_id_chunk(id_file, batch_size):
	""" 
	Chunk the pandas dataframe so not everything is read into memory

    Keyword Arguments:
    id_file -- the file to read through pandas
    batch_size -- the size of each chunk
    """
	for id_batch in pd.read_csv(id_file, sep="\t", chunksize=batch_size):
		yield id_batch

def download_full_text(ids_file, document_batch, document_output):
	"""
    Download full text from Pubtator Central.
    This section involves heavy api calls and subject to get blocked.
    Email the researchers at pubtator if this script continues to be blocked

    Keywords arguments:
    ids_file -- The path containing the pmids to pmcids map
    document_batch -- the size of each id batch
    document_output -- the path to output the formatted data
    """

	# Pubtator supports biocxml and json 
	# This script only uses biocxml 
	pubtator_central_api = "https://www.ncbi.nlm.nih.gov/research/pubtator-api/publications/export/biocxml?"

	with open(f"{document_output}", "wb") as xml_file:
		for idx, pmcid_batch_df in tqdm.tqdm(enumerate(read_id_chunk(ids_file, document_batch))):
			query = f"{pubtator_central_api}pmcids={','.join(pmcid_batch_df.pmcids.values)}"
			response = requests.get(query)

			if response.status_code != 200:
				raise Exception(response.text)

			if idx == 0:
				root = ET.fromstring(
						bytes(response.text, encoding="utf8")
					)

			else:
				append_root = ET.fromstring(
						bytes(response.text, encoding="utf8")
					)

				for document in append_root.findall(".//document"):
					root.append(document)

		xml_file.write(ET.tostring(root, pretty_print=True))


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Extracts the annotations from the BioC xml format')
	parser.add_argument("--input", help="a tsv file that contains pmids to query for full text", required=True)
	parser.add_argument("--document_batch", help="the number of documents to query at once", default=100, type=int)
	parser.add_argument("--output", help="the name of the outputfile containing full text documents", default="pubtator_full_text_docs")
	args = parser.parse_args()

	download_full_text(args.input, args.document_batch, args.output)
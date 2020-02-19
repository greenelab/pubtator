import argparse
from pathlib import Path
import requests
import time
import os

import lxml.etree as ET
from lxml.etree import XMLSyntaxError
import pandas as pd
from ratelimit import limits, sleep_and_retry
import tqdm


QUERY_RATE = 60*15
@sleep_and_retry
@limits(calls=10000, period=QUERY_RATE)
def call_api(url):
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(response.text)

    return response

def read_id_chunk(id_file, batch_size):
    """ 
    Chunk the pandas dataframe so not everything is read into memory

    Keyword Arguments:
    id_file -- the file to read through pandas
    batch_size -- the size of each chunk
    """
    for id_batch in pd.read_csv(id_file, sep="\t", chunksize=batch_size):
        yield id_batch

def download_full_text(ids_file, document_batch, temp_dir):
    """
    Download full text from Pubtator Central.
    This section involves heavy api calls and subject to get blocked.
    Email the researchers at pubtator if this script continues to be blocked

    Keywords arguments:
    ids_file -- The path containing the pmids to pmcids map
    document_batch -- the size of each id batch
    temp_dir -- the directory to hold full text batches from pubtator central api
    """

    # Pubtator supports biocxml and json 
    # This script only uses biocxml 
    pubtator_central_api = "https://www.ncbi.nlm.nih.gov/research/pubtator-api/publications/export/biocxml?"

    for idx, pmcid_batch_df in tqdm.tqdm(enumerate(read_id_chunk(ids_file, document_batch))):
        query = f"{pubtator_central_api}pmcids={','.join(pmcid_batch_df.PMCID.values)}"
        
        response = call_api(query)

        with open(f"{temp_dir}/batch_{idx}.xml", "wb") as xml_file:
            try:
                root = ET.fromstring(
                    bytes(response.text, encoding="utf8")
                )

                xml_file.write(ET.tostring(root, pretty_print=True))
            except Exception as e:
                print(query)

def merge_full_text(temp_dir, output):
    """
    Download full text from Pubtator Central.
    This section involves heavy api calls and subject to get blocked.
    Email the researchers at pubtator if this script continues to be blocked

    Keywords arguments:
    temp_dir -- The path containing the pmids to pmcids map
    output -- the size of each id batch
    """
    batch_files = Path().rglob(f"{temp_dir}/*.xml")

    with open(output, "wb") as xml_file:
        first_file = True
        
        for file in tqdm.tqdm(batch_files):
            try:
                tree = ET.parse(str(file.resolve()))
                root = tree.getroot()
                
                # Write Header for output
                if first_file:
                    # write opening tag to file
                    xml_file.write(b"<collection>\n")

                    for tag in root.getchildren():
                        if tag.tag == "date":
                            tag.text = time.strftime("%Y/%m/%d")

                        # skip document tags will incorporate later
                        if tag.tag == "document":
                            break

                        xml_file.write(ET.tostring(tag, pretty_print=True))
                    
                    first_file = False

                for document in root.xpath("document"):
                    xml_file.write(ET.tostring(document, pretty_print=True))
            
            except XMLSyntaxError as e:
                print(f"Please check {file}! There is an error at: {e}")
                print("I am skipping this file.")

        xml_file.write(b"</collection>\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extracts the annotations from the BioC xml format')
    parser.add_argument("--input", help="a tsv file that contains pmids to query for full text", required=True)
    parser.add_argument("--document_batch", help="the number of documents to query at once", default=100, type=int)
    parser.add_argument("--temp_dir", help="The directory to store the temporary files", required=True, type=str)
    parser.add_argument("--output", help="the name of the outputfile containing full text documents", default="pubtator_full_text.xml")
    args = parser.parse_args()

    download_full_text(args.input, args.document_batch, args.temp_dir)
    merge_full_text(args.temp_dir, args.output)

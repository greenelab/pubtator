import argparse
import csv

from lxml import etree as ET
import tqdm

import utilities

def extract_annotations(xml_path, tsv_path):
    """
    Extract the annotations from pubtator xml formatted file
    Outputs a TSV file with the following header terms:
    Document - the corresponding pubmed id
    Type - the type of term (i.e. Chemical, Disease, Gene etc.)
    ID - the appropiate MESH or NCBI ID if known
    Offset - the character position where the term starts
    End - the character position where the term ends

    Keywords arguments:
    xml_path -- The path to the xml data file
    tsv_path -- the path to output the formatted data
    """
    xml_opener = utilities.get_opener(xml_path)
    csv_opener = utilities.get_opener(tsv_path)
    with xml_opener(xml_path, "rb") as xml_file, csv_opener(tsv_path, "wt") as tsv_file:
        fieldnames = ['Document', 'Type', 'ID', 'Offset', 'End']
        writer = csv.DictWriter(tsv_file, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        tag_generator = ET.iterparse(xml_file, tag="document")

        for event, document in tqdm.tqdm(tag_generator):
            pubmed_id = document[0].text

            # cycle through all the annotation tags contained within document tag
            for annotation in document.iter('annotation'):

                # not all annotations will contain an ID
                if len(annotation) <= 3:
                    continue

                for infon in annotation.iter('infon'):
                    if infon.attrib["key"] == "type":
                        ant_type = infon.text
                    else:
                        ant_id = infon.text

                location, = annotation.iter('location')
                offset = int(location.attrib['offset'])
                end = offset + int(location.attrib['length'])
                row = {'Document': pubmed_id, 'Type': ant_type, 'ID': ant_id, 'Offset': offset, 'End': end}
                writer.writerow(row)

            # prevent memory overload
            document.clear()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Export tags in a BioC XML file to a TSV table')
    parser.add_argument("--input", help="Path for the input BioC XML file", type=str, required=True)
    parser.add_argument("--output", nargs="?", help="Path for the output TSV file", required=True)

    args = parser.parse_args()

    extract_annotations(xml_path=args.input, tsv_path=args.output)

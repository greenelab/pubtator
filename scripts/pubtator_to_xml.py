import argparse
import csv
import os
import re
import time

from bioc import BioCWriter, BioCCollection, BioCDocument, BioCPassage
from bioc import BioCAnnotation, BioCLocation
from itertools import groupby
from lxml.builder import E
from lxml.etree import tostring
import tqdm

import utilities


def bioconcepts2pubtator_annotations(tag, index, chemical_map, disease_map):
    """Bioconcepts to Annotations
    Specifically for bioconcepts2pubtator and converts each annotation
    into an annotation object that BioC can parse.

    Keyword Arguments:
    tag -- the annotation line that was parsed into an array
    index -- the id of each document specific annotation
    """

    annt = BioCAnnotation()
    annt.id = str(index)
    annt.infons["type"] = tag["type"]

    # source_label = "MESH"
    source_label = "HETNET"

    # If the annotation type is a Gene,Species, Mutation, SNP
    # Write out relevant tag
    tag_type = tag['type'] or ''
    tag_id = tag['tag_id']

    if tag_type == "Gene":
        annt.infons["NCBI Gene"] = tag_id

    elif tag_type == "Species":
        annt.infons["NCBI Species"] = tag_id

    elif "Mutation" in tag_type:
        annt.infons["tmVar"] = tag_id

    elif "SNP" in tag_type:
        annt.infons["tmVar"] = tag_id

    elif "Chemical" in tag_type:
            tag_type_to_correct_labels(tag, tag_type, tag_id, source_label, chemical_map, annt)

    elif "Disease" in tag_type:
            tag_type_to_correct_labels(tag, tag_type, tag_id, source_label, disease_map, annt)
    else:
        print("Error no identifiable tag. Skipping!!")

    location = BioCLocation()
    location.offset = str(tag["start"])
    location.length = str(len(tag["term"]))
    annt.locations.append(location)
    annt.text = tag["term"]
    return annt


def tag_type_to_correct_labels(tag, tag_type, tag_id, source_label, id_map, annt):
    """ This function will assign each tag the appropiate hetnet label given
        some context conditions.

    """

    # If there is no MESH ID for an annotation
    if tag_id:

        # check to see if there are multiple mesh tags
        if "|" in tag_id:

            # Write out each MESH id as own tag
            for tag_num, ids in enumerate(tag_id.split("|")):

                # Some ids dont have the MESH:#### form so added case to that
                if ":" not in ids:
                    if ids in id_map:
                        annt.infons["{} {}".format(source_label, tag_num)] = id_map[term_id]
                    else:
                        annt.infons["{} {}".format(source_label, tag_num)] = tag_id
                else:
                    term_type, term_id = ids.split(":")
                    annt.infons["{} {}".format(term_type, tag_num)] = term_id
        else:
            # Some ids dont have the MESH:#### form so added case to that
            if ":" in tag_id:
                term_type, term_id = tag_id.split(":")

                if term_id in id_map:
                    annt.infons[source_label] = id_map[term_id]
                else:
                    annt.infons[term_type] = term_id

            else:
                if tag_id in id_map:
                    annt.infons[source_label] = id_map[tag_id]
                else:
                    annt.infons["MESH"] = tag_id
    else:
        annt.infons["MESH"] = "Unknown"

    return


def pubtator_stanza_to_article(lines):
    """Article Generator

    Returns an article that is a dictionary with the following keywords:
    pubmed_id - a document identifier
    Title- the title string
    Abstract-  the abstract string
    Title_Annot- A filtered list of tags specific to the title
    Abstract_Annot- A filtered list of tags specific to the abstract

    Keywords:
    lines - this is a list of file lines passed from bioconcepts2pubtator_offsets function
    """
    article = {}

    # title
    title_heading = lines[0].split('|')
    article["pubmed_id"] = title_heading[0]
    article["title"] = title_heading[2]
    title_len = len(title_heading[2])

    # abstract
    abstract_heading = lines[1].split("|")
    article["abstract"] = abstract_heading[2]

    # Clean up the term lines
    remove_chars = '\"'
    annot_lines = clean_up_annotations(lines[2:])

    # set up the csv reader
    annts = csv.DictReader(annot_lines, fieldnames=['pubmed_id', 'start', 'end', 'term', 'type', 'tag_id'], delimiter="\t")
    annts = list(annts)

    for annt in annts:
        for key in 'start', 'end':
            annt[key] = int(annt[key])
    annts.sort(key=lambda x: x["start"])
    article["title_annot"] = filter(lambda x: x["start"] < title_len, annts)
    article["abstract_annot"] = filter(lambda x: x["start"] > title_len, annts)

    return article


def read_bioconcepts2pubtator_offsets(path):
    """Bioconcepts to pubtator

    Yields an article that is a dictionary described in the article generator
    function.

    Keywords:
    path - the path to the bioconcepts2putator_offset file (obtained from pubtator's ftp site: ftp://ftp.ncbi.nlm.nih.gov/pub/lu/PubTator/)
    """
    opener = utilities.get_opener(path)
    f = opener(path, "rt")

    lines = (line.rstrip() for line in f)

    for k, g in groupby(lines, key=bool):
        # Group articles based on empty lines as separators. Only pass
        # on non-empty lines.
        g = list(g)
        if g[0]:
            yield pubtator_stanza_to_article(g)

    f.close()


def load_checmical_map():
    """ Load the chebi-drugbank (hetnet) id mapping table.
    Return a dictionary: key - chebi_id, value - drugbank_id
    """
    with open("../chemical_hetnet_ids.tsv") as id_file:
        id_reader = csv.DictReader(id_file, delimiter="\t")
        chem_map = {row["chebi_id"]: row["drugbank_id"] for row in id_reader}
    return chem_map


def load_disease_map():
    """
    Load the mesh-hetnet id mapping table.
    Return a dictionary of key - disease terms value - hetnet id
    """
    with open("../disease_hetnet_ids.tsv") as id_file:
        id_reader = csv.DictReader(id_file, delimiter="\t")
        disease_map = {row["resource_id"]: row["doid_code"] for row in id_reader}
    return disease_map


def clean_up_annotations(lines):
    """
        Cleans up the annotations that have a problem character.
        Pubtator's annotations don't cover the full quotation which
        causes the dict reader to not process the input line correctly.
        Therefore, this function is designed to remove these bad characters.

        Keyword Arguments:
        lines - a list of annotation lines
    """

    for index, annt in enumerate(lines):
        if annt.count('\"') == 1:
            lines[index] = re.sub('\"', '', annt)
    return lines


def convert_pubtator(input_path, output_path):
    """Convert pubtators annotation list to BioC XML

    Keyword Arguments
    input_file -- the path of pubtators annotation file
    output_file -- the path to output the BioC XML file
    """

    # Load the hetnet mappings here
    chemical_map = load_checmical_map()
    disease_map = load_disease_map()

    # Set up the generator and file reader
    article_generator = read_bioconcepts2pubtator_offsets(input_path)
    opener = utilities.get_opener(output_path)

    with opener(output_path, 'wb') as xml_file:

        # Set up BioCWriter to write specifically Pubtator
        # Can change to incorporate other sources besides pubtator
        writer = BioCWriter()
        writer.collection = BioCCollection()
        collection = writer.collection
        collection.date = time.strftime("%Y/%m/%d")
        collection.source = "Pubtator"
        collection.key = "Pubtator.key"

        # Have to manually do this because hangs otherwise
        # Write the head of the xml file
        xml_shell = writer.tostring('UTF-8')
        *xml_head, xml_tail = xml_shell.rstrip().split(b'\n')
        for line in xml_head:
            xml_file.write(line + b'\n')

        # Write each article in BioC format
        for article in tqdm.tqdm(article_generator):

            document = BioCDocument()
            document.id = article["pubmed_id"]

            title_passage = BioCPassage()
            title_passage.put_infon('type', 'title')
            title_passage.offset = '0'
            title_passage.text = article["title"]

            abstract_passage = BioCPassage()
            abstract_passage.put_infon('type', 'abstract')
            abstract_passage.offset = article["abstract"]
            abstract_passage.text = article["abstract"]

            id_index = 0
            for tag in article["title_annot"]:
                title_passage.annotations.append(bioconcepts2pubtator_annotations(tag, id_index, chemical_map, disease_map))
                id_index += 1

            for tag in article["abstract_annot"]:
                abstract_passage.annotations.append(bioconcepts2pubtator_annotations(tag, id_index, chemical_map, disease_map))
                id_index += 1

            document.add_passage(title_passage)
            document.add_passage(abstract_passage)

            step_parent = E('collection')
            writer._build_documents([document], step_parent)
            xml_file.write(tostring(step_parent[0], pretty_print=True))
            step_parent.clear()

        # Write the closing tag of the xml document
        xml_file.write(xml_tail + b'\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extracts the annotations from the BioC xml format')
    parser.add_argument("--documents", help="Path pointing to input file.", required=True)
    parser.add_argument("--output", help="Path for destination of output.", required=True)
    args = parser.parse_args()

    convert_pubtator(args.documents, args.output)

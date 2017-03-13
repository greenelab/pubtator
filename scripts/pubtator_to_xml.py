import argparse
import csv
import time

from bioc import BioCWriter, BioCCollection, BioCDocument, BioCPassage
from bioc import BioCAnnotation, BioCLocation
from itertools import groupby
from lxml.builder import E
from lxml.etree import tostring
import tqdm

import utilities


def bioconcepts2pubtator_annotations(tag, index):
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

    else:
        # If there is no MESH ID for an annotation
        if tag_id:
            # check to see if there are multiple mesh tags
            if "|" in tag_id:
                # Write out each MESH id as own tag
                for tag_num, ids in enumerate(tag_id.split("|")):
                    # Some ids dont have the MESH:#### form so added case to that
                    if ":" not in ids:
                        annt.infons["MESH {}".format(tag_num)] = tag_id
                    else:
                        term_type, term_id = ids.split(":")
                        annt.infons["{} {}".format(term_type, tag_num)] = term_id
            else:
                # Some ids dont have the MESH:#### form so added case to that
                if ":" in tag_id:
                    term_type, term_id = tag_id.split(":")
                    annt.infons[term_type] = term_id
                else:
                    annt.infons["MESH"] = tag_id
        else:
            annt.infons["MESH"] = "Unknown"

    location = BioCLocation()
    location.offset = str(tag["start"])
    location.length = str(len(tag["term"]))
    annt.locations.append(location)
    annt.text = tag["term"]
    return annt


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

    # set up the csv reader
    annts = csv.DictReader(lines[2:], fieldnames=['pubmed_id', 'start', 'end', 'term', 'type', 'tag_id'], delimiter="\t")
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


def convert_pubtator(input_path, output_path):
    """Convert pubtators annotation list to BioC XML

    Keyword Arguments:
    input_file -- the path of pubtators annotation file
    output_file -- the path to output the BioC XML file
    """

    # Set up BioCWriter to write specifically Pubtator
    # Can change to incorporate other sources besides pubtator
    writer = BioCWriter()
    writer.collection = BioCCollection()
    collection = writer.collection
    collection.date = time.strftime("%Y/%m/%d")
    collection.source = "Pubtator"
    collection.key = "Pubtator.key"

    opener = utilities.get_opener(output_path)
    with opener(output_path, 'wb') as xml_file:

        # Have to manually do this because hangs otherwise
        # Write the head of the xml file
        xml_shell = writer.tostring('UTF-8')
        *xml_head, xml_tail = xml_shell.rstrip().split(b'\n')
        for line in xml_head:
            xml_file.write(line + b'\n')

        article_generator = read_bioconcepts2pubtator_offsets(input_path)
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
                title_passage.annotations.append(bioconcepts2pubtator_annotations(tag, id_index))
                id_index += 1

            for tag in article["abstract_annot"]:
                abstract_passage.annotations.append(bioconcepts2pubtator_annotations(tag, id_index))
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

import argparse
import csv
import shelve

import tqdm


def store_annotations(input_file, output_file):
    """ Stores annotations into python's shelve module (Dictionary)

    Keywords:
    input_file - the name of the element tagged file
    output_file - the name of the file to be written out
    """
    with open(input_file, 'r') as g:
        d = shelve.open(output_file)
        reader = csv.DictReader(g, delimiter='\t')
        temp = []
        seen = ''
        for r in tqdm.tqdm(reader):
            if seen != r['Document']:
                if seen != '':
                    d[seen] = temp
                    temp = []
                seen = r['Document']
            temp.append(r)
        d[r['Document']] = temp
    d.close()

# Main
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Converts the Element Tag TSV file into a Shelf')
    parser.add_argument("--input", help="File path pointing to the tag tsv file.", type=str, required=True)
    parser.add_argument("--output", nargs="?", help="File path for destination of output.", required=True)

    args = parser.parse_args()

    store_annotations(args.input, args.output)
    
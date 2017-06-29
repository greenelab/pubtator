import argparse

import pandas as pd


def filter_tags(infile, outfile):
    extracted_tag_df = pd.read_table(infile)
    hetnet_chemical_df = load_chemical_df()
    hetnet_disease_df = load_disease_df()
    hetnet_gene_df = load_gene_df()

    # Covert chemical IDs
    chemical_merged_df = pd.merge(extracted_tag_df[extracted_tag_df["type"] == "Chemical"], hetnet_chemical_df[["drugbank_id", "identifier"]], left_on="identifier", right_on="identifier")
    chemical_merged_df = chemical_merged_df.drop_duplicates()
    chemical_merged_df["type"] = "Compound"
    chemical_merged_df = chemical_merged_df[["pubmed_id", "type", "offset", "end", "drugbank_id"]].rename(columns={"drugbank_id": "identifier"})

    # Convert Disease IDs
    disease_merged_df = pd.merge(extracted_tag_df[extracted_tag_df["type"] == "Disease"], hetnet_disease_df[["doid_code", "resource_id"]], left_on="identifier", right_on="resource_id").drop_duplicates()
    disease_merged_df = disease_merged_df[["pubmed_id", "type", "offset", "end", "doid_code"]].rename(columns={"doid_code": "identifier"})

    # Verify Gene IDs are human genes
    gene_df = extracted_tag_df[extracted_tag_df["type"] == "Gene"]
    gene_final_df = gene_df[gene_df["identifier"].isin(hetnet_gene_df["GeneID"])]

    final_df = gene_final_df
    final_df = final_df.append(chemical_merged_df)
    final_df = final_df.append(disease_merged_df)

    final_df[["pubmed_id", "type", "identifier", "offset", "end"]].sort_values(["pubmed_id", "offset"]).to_csv(args.output, sep="\t", index=False)


def load_disease_df():
    """
    Load the mesh-hetnet id mapping table.
    Return a dataframe of id mappings
    """
    url = 'https://raw.githubusercontent.com/dhimmel/disease-ontology/052ffcc960f5897a0575f5feff904ca84b7d2c1d/data/xrefs-prop-slim.tsv'
    disease_df = pd.read_table(url)
    return disease_df[disease_df["resource"] == "MSH"]


def load_chemical_df():
    """
    Loads the chebi-mesh-drugbank id mapping table
    Return a dataframe with id mappings
    """
    return pd.read_table("mapper/drugbank_mapper.tsv")


def load_gene_df():
    """
    Loads the gene table from hetnets
    Return a dataframe with the gene ids
    """
    url = 'https://raw.githubusercontent.com/dhimmel/entrez-gene/a7362748a34211e5df6f2d185bb3246279760546/data/genes-human.tsv'
    gene_df = pd.read_table(url).astype({"GeneID": str})
    return gene_df[gene_df["type_of_gene"] == "protein-coding"]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Filter extracted tags to contain Hetnet IDs in a TSV table')
    parser.add_argument("--input", help="Path for the tsv tag table", type=str, required=True)
    parser.add_argument("--output", nargs="?", help="Path for the output TSV file", type=str, required=True)

    args = parser.parse_args()

    filter_tags(infile=args.input, outfile=args.output)

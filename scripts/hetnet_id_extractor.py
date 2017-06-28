import argparse

import pandas as pd


def filter_tags(infile, outfile):
    extracted_tag_df = pd.read_csv(infile, sep="\t")
    hetnet_chemical_df = load_chemical_df()
    hetnet_disease_df = load_disease_df()
    hetnet_gene_df = load_gene_df()

    # Convert Chebi IDs
    chebi_merged_df = pd.merge(extracted_tag_df, hetnet_chemical_df[["drugbank_id", "chebi_id"]], left_on="ID", right_on="chebi_id")
    chebi_merged_df["Type"] = "Compound"
    chebi_merged_df = chebi_merged_df[["Document", "Type", "Offset", "End", "chebi_id"]].rename(columns={"chebi_id": "ID"})

    # Convert MeSH iDs
    mesh_merged_df = pd.merge(extracted_tag_df, hetnet_chemical_df[["drugbank_id", "MeSH"]], left_on="ID", right_on="MeSH").drop_duplicates()
    mesh_merged_df["Type"] = "Compound"
    mesh_merged_df = mesh_merged_df[["Document", "Type", "Offset", "End", "MeSH"]].rename(columns={"MeSH": "ID"})

    # Convert Disease IDs
    disease_merged_df = pd.merge(extracted_tag_df, hetnet_disease_df[["doid_code", "resource_id"]], left_on="ID", right_on="resource_id").drop_duplicates()
    disease_merged_df = disease_merged_df[["Document", "Type", "Offset", "End", "doid_code"]].rename(columns={"doid_code": "ID"})

    # Verify Gene IDs are human genes
    gene_df = extracted_tag_df[extracted_tag_df["Type"] == "Gene"]
    gene_final_df = gene_df[gene_df["ID"].isin(hetnet_gene_df["GeneID"])]

    final_df = gene_final_df
    final_df = final_df.append(mesh_merged_df)
    final_df = final_df.append(chebi_merged_df).drop_duplicates()
    final_df = final_df.append(disease_merged_df)

    final_df[["Document", "Type", "ID", "Offset", "End"]].to_csv(args.output, sep="\t", index=False)


def load_disease_df():
    """
    Load the mesh-hetnet id mapping table.
    Return a dataframe of id mappings
    """
    url = 'https://raw.githubusercontent.com/dhimmel/disease-ontology/052ffcc960f5897a0575f5feff904ca84b7d2c1d/data/xrefs-prop-slim.tsv'
    return pd.read_csv(url, sep="\t")


def load_chemical_df():
    """
    Loads the chebi-mesh-drugbank id mapping table
    Return a dataframe with id mappings
    """
    return pd.read_csv("mapper/drugbank_mapper.tsv", sep="\t").astype({"chebi_id": object})


def load_gene_df():
    """
    Loads the gene table from hetnets
    Return a dataframe with the gene ids
    """
    url = 'https://raw.githubusercontent.com/dhimmel/entrez-gene/a7362748a34211e5df6f2d185bb3246279760546/data/genes-human.tsv'
    return pd.read_csv(url, sep="\t").astype({"GeneID": str})

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Filter extracted tags to contain Hetnet IDs in a TSV table')
    parser.add_argument("--input", help="Path for the tsv tag table", type=str, required=True)
    parser.add_argument("--output", nargs="?", help="Path for the output TSV file", type=str, required=True)

    args = parser.parse_args()

    filter_tags(infile=args.input, outfile=args.output)

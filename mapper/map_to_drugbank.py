import pandas as pd

# Map from DrugBank to MeSH using DrugCentral
url = 'https://github.com/olegursu/drugtarget/blob/9a6d84bed8650c6c507a2d3d786814c774568610/identifiers.tsv?raw=true'
drug_map_df = pd.read_table(url)

drug_bank_df = drug_map_df[drug_map_df.ID_TYPE == 'DRUGBANK_ID'].rename(columns={"IDENTIFIER": "drugbank_id"})
mesh_map_df = drug_map_df[drug_map_df.ID_TYPE.str.contains('MESH')].rename(columns={"IDENTIFIER": "identifier"})
drug_bank_mesh_df = pd.merge(drug_bank_df[["DRUG_ID", "drugbank_id"]], mesh_map_df[["DRUG_ID", "identifier"]], on="DRUG_ID")
drug_bank_mesh_df["source"] = "MESH"
drug_bank_mesh_df = drug_bank_mesh_df.rename({})

# Grab the chebi to DB mapper
url = 'https://raw.githubusercontent.com/dhimmel/drugbank/7b94454b14a2fa4bb9387cb3b4b9924619cfbd3e/data/mapping/chebi.tsv'
chebi_map_df = pd.read_table(url)
chebi_map_df["chebi_id"] = chebi_map_df["chebi_id"].astype(object)
chebi_map_df = chebi_map_df.rename(columns={"chebi_id": "identifier"})
chebi_map_df["source"] = "CHEBI"

final_df = drug_bank_mesh_df[["drugbank_id", "identifier", "source"]].append(chebi_map_df)
final_df.to_csv("mapper/drugbank_mapper.tsv", sep="\t", index=False)

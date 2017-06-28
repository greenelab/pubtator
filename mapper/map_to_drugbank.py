import pandas as pd

# Map from DrugBank to MeSH using DrugCentral
url = 'https://github.com/olegursu/drugtarget/blob/9a6d84bed8650c6c507a2d3d786814c774568610/identifiers.tsv?raw=true'
drug_map_df = pd.read_table(url)
drug_map_df = drug_map_df[drug_map_df.ID_TYPE.str.contains('MESH')][['DRUG_ID', 'IDENTIFIER']].rename(columns={'IDENTIFIER': 'MeSH'}).merge(
drug_map_df[drug_map_df.ID_TYPE == 'DRUGBANK_ID'][['DRUG_ID', 'IDENTIFIER']].rename(columns={'IDENTIFIER': 'drugbank_id'})
).drop('DRUG_ID', axis='columns')

# Grab the chebi to DB mapper
url = 'https://raw.githubusercontent.com/dhimmel/drugbank/7b94454b14a2fa4bb9387cb3b4b9924619cfbd3e/data/mapping/chebi.tsv'
chebi_map_df = pd.read_table(url)
chebi_map_df["chebi_id"] = chebi_map_df["chebi_id"].astype(object)

merged_df = pd.merge(chebi_map_df, drug_map_df, on="drugbank_id", how="outer")
merged_df.to_csv("drugbank_mapper.tsv", sep="\t", index=False)
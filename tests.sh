set -o errexit

# Convert pubtator format to BioC XML
python scripts/pubtator_to_xml.py \
  	--documents data/example/1-sample-annotations.txt \
 	--output data/example/2-sample-docs.xml

# Extract tags from the BioC XML 
python scripts/extract_tags.py \
 	--input data/example/2-sample-docs.xml \
 	--output data/example/3-sample-tags.tsv

# Filter-Convert tags to Hetnet IDs
python scripts/hetnet_id_extractor.py \
 	--input data/example/3-sample-tags.tsv \
 	--output data/example/4-hetnet-tags.tsv

python scripts/map_ids.py \
	--input data/example/3-sample-tags.tsv \
	--output data/example/5-sample-pmids-to-pmcids.tsv \

python scripts/download_full_text.py \
	--input data/example/5-sample-pmids-to-pmcids.tsv \
	--output data/example/6-sample-full-text.xml \
	--temp_dir data/temp

# Extract tags from the BioC XML 
python scripts/extract_tags.py \
 	--input data/example/6-sample-full-text.xml \
 	--output data/example/7-sample-full-text-tags.tsv

# Filter-Convert tags to Hetnet IDs
python scripts/hetnet_id_extractor.py \
 	--input data/example/7-sample-full-text-tags.tsv \
 	--output data/example/8-hetnet-full-text-tags.tsv

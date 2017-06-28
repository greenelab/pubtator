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
  
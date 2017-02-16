# Exit on an error
set -o errexit

# PubTator FTP download
FTP_URL=ftp://ftp.ncbi.nlm.nih.gov/pub/lu/PubTator
wget \
  --timestamping \
  --directory-prefix=download \
  --output-file=download/bioconcepts2pubtator_offsets.gz.log \
  $FTP_URL/bioconcepts2pubtator_offsets.gz

# Convert pubtator format to BioC XML
python scripts/pubtator_to_xml.py \
  --documents download/bioconcepts2pubtator_offsets.gz \
  --output data/pubtator-docs.xml.xz

# Extract tags from the BioC XML to a TSV
python scripts/extract_tags.py \
  --input data/pubtator-docs.xml.xz \
  --output data/pubtator-tags.tsv.xz

# Exit on an error
set -o errexit

if [ "$1" == "--pubtator" ]; then
  # PubTator FTP download
  FTP_URL=ftp://ftp.ncbi.nlm.nih.gov/pub/lu/PubTator;

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

  # Extract hetnet tags from the pubtator tags
  python scripts/hetnet_id_extractor.py \
    --input data/pubtator-tags.tsv.xz \
    --output data/pubtator-hetnet-tags.tsv.xz

else
  # PubTator Central FTP download
  FTP_URL=ftp://ftp.ncbi.nlm.nih.gov/pub/lu/PubTatorCentral;

  wget \
    --timestamping \
    --directory-prefix=download \
    --output-file=download/bioconcepts2pubtatorcentral_offset.gz.log \
    $FTP_URL/bioconcepts2pubtatorcentral.offset.gz

  # Convert pubtator format to BioC XML
  python scripts/pubtator_to_xml.py \
    --documents download/bioconcepts2pubtatorcentral.offset.gz \
    --output data/pubtator-central-docs.xml.xz

  # Extract tags from the BioC XML to a TSV
  python scripts/extract_tags.py \
    --input data/pubtator-central-docs.xml.xz \
    --output data/pubtator-central-tags.tsv.xz

  # Extract hetnet tags from the pubtator tags
  python scripts/hetnet_id_extractor.py \
    --input data/pubtator-central-tags.tsv.xz \
    --output data/pubtator-central-hetnet-tags.tsv.xz

  # Grab ids with full text
  python scripts/map_ids.py \
    --input data/pubtator-central-tags.tsv.xz \
    --output data/pubtator-pmids-to-pmcids.tsv

  # Download full text from pubtator central
  python scripts/download_full_text.py \
    --input data/pubtator-pmids-to-pmcids.tsv \
    --document_batch 100 \
    --output data/pubtator-central-full-text.xml

  # Extract tags from the BioC XML 
  python scripts/extract_tags.py \
    --input data/pubtator-central-full-text.xml \
    --output data/pubtator-central-full-text-tags.tsv.xz

  # Filter-Convert tags to Hetnet IDs
  python scripts/hetnet_id_extractor.py \
    --input data/pubtator-central-full-text-tags.tsv.xz \
    --output data/pubtator-central-full-hetnet-tags.tsv.xz

fi

# Converting Pubtator Annotations to BioC XML

This folder conatins two scirpts that will convert [pubtator to bioC xml](pubtator_to_xml.py) and also[extract annoations](extract_tags.py) for snorkel to use.
1. To run the pubtator converter use the following command:
``python pubtator_to_xml.py --documents example/1-sample-annotations.txt --output example/2-sample-docs.xml``

2. To extract annotations from the BioC format use the following command:
``python extract_tags.py --input example/2-sample-docs.xml --output example/3-sample-tags.tsv`` 
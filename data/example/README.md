# Converting Pubtator Annotations to BioC XML

This folder conatins two scirpts one that will convert [pubtator to bioC xml](pubtator_to_xml.py) and the other will [extract annoations](extract_tags.py) for snorkel to use.  
  
To run the pubtator converter use the following command:  
  
```
python ../../scripts/pubtator_to_xml.py --documents 1-sample-annotations.txt --output 2-sample-docs.xml
```  
  
To extract annotations from the BioC format use the following command:  
```
python ../../scripts/extract_tags.py --input 2-sample-docs.xml --output 3-sample-tags.tsv
``` 

To generate the python shelf files use the following command:
```
python ../../scripts/shelve_tags.py --input 3-sample-tags.tsv --output 4-sample-shelve
```

# Configuration Files Explained

This file explains the pipeline steps and parameters needed for each step.
**Note: any added parameter or step will be ignored unless `execute.py` is manually changed.**

## Repository Download

This is the first step of the Pubtator pipeline.
Basically this step downloads Pubtator Central's annotation file from their ftp server.

Following Parameters for this section:
| Param | Description | Accepted Values |
| --- | --- | --- |
| url | the url to download the file from | a string with a url path |
| download_folder | the folder to hold the downloaded file | a string name for the folder |
| skip | tell execute.py to ignore this step and contine | true or false |

## Pubtator to XML

This is the second step of the Pubtator pipeline.
This step converts Pubtator/Pubtator Central's annotation file into xml format.
**Note: This step may take awhile to complete**

Following Parameters for this section:
| Param | Description | Accepted Values |
| --- | --- | --- |
| documents | The file path pointing to the downloaded file from the previous step. | a string for the file path |
| output | The file path to save the xml file. Make sure to keep the xz extension. | a string for the file path |
| skip | Tell execute.py to ignore this step and contine | true or false |

## Extract Tags

This is the second step of the Pubtator pipeline.
This step extracts Pubtator/Pubtator Central's annotations from the xml file.
It outputs a tsv file that contains all extracted annotation.
**Note: This step may take awhile to complete**

Following Parameters for this section:
| Param | Description | Accepted Values |
| --- | --- | --- |
| input | The file path pointing to the xml file in previouss step. Make sure to keep the xz extension. | a string for the file path |
| output | The file path to save the tsv file. Make sure to keep the xz extension. | a string for the file path |
| skip | Tell execute.py to ignore this step and contine | true or false |

## Hetnet ID Extractor

This is the third step of the Pubtator pipeline.
This step filters out extracted annotations to only include tags within [Hetionet's Database](https://het.io/).

Following Parameters for this section:
| Param | Description | Accepted Values |
| --- | --- | --- |
| input | The file path pointing to the tsv file in previous step. Make sure to keep the xz extension. | a string for the file path |
| output | The file path to save the tsv file. Make sure to keep the xz extension. | a string for the file path |
| skip | Tell execute.py to ignore this step and contine | true or false |

## Map PMIDS to PMCIDS

This is the forth step of the Pubtator pipeline.
This step querys NCBI's pmid to pmcid mapper in order to grab PMCIDS.
**Note: To download full text you will need to have PMCIDS. PMIDS will not work.**

Following Parameters for this section:
| Param | Description | Accepted Values |
| --- | --- | --- |
| input | The file path pointing to the tsv file in extract tags step. Make sure to keep the xz extension. | a string for the file path |
| output | The file path to save the tsv file. | a string for the file path |
| debug | This is a flag for debugging purposes. Feel free to ignore and leave as false. | true or false |
| skip | Tell execute.py to ignore this step and contine | true or false |

## Download Full Text

This is the fifth step of the Pubtator pipeline.
This step queries Pubtator Central's api and downloads annotated full text if text is present.

Following Parameters for this section:
| Param | Description | Accepted Values |
| --- | --- | --- |
| input | The file path pointing to the tsv file in previous step. | a string for the file path |
| output | The file path to save the xml file. | a string for the file path |
| temp_dir | The folder to hold temporary batch files for this step of the pipeline | a string for the folder path |
| log_file | A log file that keeps track of the IDs that have already been queried. It is used to monitor progress in case the process is interrupted. Make sure it has the tsv extension. | a file path for the file |
| skip | Tell execute.py to ignore this step and contine | true or false |

## Extract Full Text Tags

This is the sixth step of the Pubtator pipeline.
This step extracts tags from full text documents.
Please refer to [Extract Tags Section](#extract-tags) for parameter details.

## Hetnet ID Extractor Full Text

This is the last step of the Pubtator pipeline.
This step filters tags to only have Hetionet tags.
Please refer to [Hetnet ID Extractor Section](#hetnet-id-extractor) for parameter details.


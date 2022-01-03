# PubTator: tagged PubMed abstracts for literature mining

[![Build Status](https://travis-ci.org/greenelab/pubtator.svg?branch=master)](https://travis-ci.org/greenelab/pubtator)

[PubTator](https://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/PubTator/) and its 2.0 version ([PubTator Central](https://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/PubTatorCentral/)) uses text mining to tag PubMed abstracts/artciles with standardized concepts. This repository retrieves and processes PubTator annotations for use in [`greenelab/snorkeling`](https://github.com/greenelab/snorkeling) and elsewhere.

# Get Started

## **Depreciation Notice**

If you have arrived at this page in order to convert Pubtator into BioCXML format, you no longer need to. 
Pubtator Central now provides their own BioCXML files which can be found [here](https://ftp.ncbi.nlm.nih.gov/pub/lu/PubTatorCentral/PubTatorCentral_BioCXML/).

## Set-up Environment

### Conda

1. Install the [conda](https://conda.io) environment.
2. Create the pubtator environmenmt by running:

```sh
conda create --name pubtator python=3.8
```
3. Install packages via pip by running the following:

```sh
pip install -r requirements.txt
```

4. Activate with `conda activate pubtator`.

### Pip

1. Make sure you have python version **3.8** installed.
2. Install packages by running the following:

```sh
pip install -r requirements.txt
```


## Execution

To start processing Pubtator/Pubtator Central run the following command:

```sh
python execute.py --config config_files/pubtator_central_config.json
```

If the original Pubtator is desired replace `pubtator_central_config.json` with `pubtator_config.json`. The json file contains all the necessary parameters needed to run. More information for the json file can be found [here](config_files).

## License

This repository is dual licensed as [BSD 3-Clause](LICENSE-BSD.md) and [CC0 1.0](LICENSE-CC0.md), meaning any repository content can be used under either license. This licensing arrangement ensures source code is available under an [OSI-approved License](https://opensource.org/licenses/alphabetical), while non-code content — such as figures, data, and documentation — is maximally reusable under a public domain dedication.

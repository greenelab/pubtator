# PubTator: tagged PubMed abstracts for literature mining

[![Build Status](https://travis-ci.org/greenelab/pubtator.svg?branch=master)](https://travis-ci.org/greenelab/pubtator)

[PubTator](https://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/PubTator/) and its 2.0 version ([PubTator Central](https://www.ncbi.nlm.nih.gov/CBBresearch/Lu/Demo/PubTatorCentral/)) uses text mining to tag PubMed abstracts/artciles with standardized concepts. This repository retrieves and processes PubTator annotations for use in [`greenelab/snorkeling`](https://github.com/greenelab/snorkeling) and elsewhere.

## Environment

Install the [conda](https://conda.io) environment specified in [`environment.yml`](environment.yml) by running:

```sh
conda env create --file environment.yml
```

Activate with `conda activate pubtator`.

## Execution

To download and extract Pubator Central's data (default) run the following:

```sh
bash execute.sh {email address here}
```

If the original Pubtator is desired run the above command with the following flag: --pubtator. You do not need to provide your email address when running the first version of Pubtator.

## License

This repository is dual licensed as [BSD 3-Clause](LICENSE-BSD.md) and [CC0 1.0](LICENSE-CC0.md), meaning any repository content can be used under either license. This licensing arrangement ensures source code is available under an [OSI-approved License](https://opensource.org/licenses/alphabetical), while non-code content — such as figures, data, and documentation — is maximally reusable under a public domain dedication.

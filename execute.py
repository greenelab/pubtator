import argparse
from pathlib import Path
import json

import wget

from scripts.download_full_text import download_full_text, merge_full_text
from scripts.extract_tags import extract_annotations
from scripts.hetnet_id_extractor import filter_tags
from scripts.map_ids import map_ids
from scripts.pubtator_to_xml import convert_pubtator

parser = argparse.ArgumentParser(
    description='Runs Pubtator/Pubtator Central Parser Pipeline'
)

parser.add_argument(
    "--config", help="The config file for the extractor.", 
    default="config_files/pubtator_central_config.json"
)

args = parser.parse_args()

configuration = json.load(open(args.config, "r"))

if (
    "repository_download" in configuration and 
    not configuration["repository_download"]["skip"]
):
    print("Executing repository_download...")
    wget.download(
        configuration["repository_download"]['url'], 
        out=configuration["repository_download"]['download_folder']
    )
    
    del configuration["repository_download"]

if (
    "pubtator_to_xml" in configuration and 
    not configuration["pubtator_to_xml"]["skip"]
):
    print("Executing pubtator_to_xml...")
    convert_pubtator(
        configuration["pubtator_to_xml"]['documents'], 
        configuration["pubtator_to_xml"]['output']
    )
    
    del configuration["pubtator_to_xml"]

if (
    "extract_tags" in configuration and 
    not configuration["extract_tags"]["skip"]
):
    print("Executing extract_tags...")
    extract_annotations(
        configuration["extract_tags"]["input"], 
        configuration["extract_tags"]["output"]
    )
    
    del configuration["extract_tags"]
    
if (
    "hetnet_id_extractor" in configuration and 
    not configuration["hetnet_id_extractor"]["skip"]
):
    print("Executing hetnet_id_extractor...")
    filter_tags(
        configuration["hetnet_id_extractor"]["input"],
        configuration["hetnet_id_extractor"]["output"]
    )
    
    del configuration["hetnet_id_extractor"]
    
if (
    "map_pmids_to_pmcids" in configuration and 
    not configuration["map_pmids_to_pmcids"]["skip"]
):
    print("Executing map_pmids_to_pmcids...")
    map_ids(
        configuration["map_pmids_to_pmcids"]["input"], 
        configuration["map_pmids_to_pmcids"]["output"], 
        configuration["map_pmids_to_pmcids"]["debug"]
    )
    
    del configuration["map_pmids_to_pmcids"]
    
if (
    "download_full_text" in configuration and 
    not configuration["download_full_text"]["skip"]
):
    print("Executing download_full_text...")
    download_full_text(
        configuration["download_full_text"]["input"],
        configuration["download_full_text"]["document_batch"], 
        configuration["download_full_text"]["temp_dir"],
        configuration["download_full_text"]["log_file"]
    )
    
    merge_full_text(
        configuration["download_full_text"]["temp_dir"], 
        configuration["download_full_text"]["output"]
    )
    
    del configuration["download_full_text"]
    
if (
    "extract_full_text_tags" in configuration and 
    not configuration["extract_full_text_tags"]["skip"]
):
    print("Executing extract_full_text_tags...")
    extract_annotations(
        configuration["extract_full_text_tags"]["input"], 
        configuration["extract_full_text_tags"]["output"]
    )
    
    del configuration["extract_full_text_tags"]

if (
    "hetnet_id_extractor_full_text" in configuration and 
    not configuration["hetnet_id_extractor_full_text"]["skip"]
):
    print("Executing hetnet_id_extractor_full_text...")
    filter_tags(
        configuration["hetnet_id_extractor_full_text"]["input"], 
        configuration["hetnet_id_extractor_full_text"]["output"]
    )
    
    del configuration["hetnet_id_extractor_full_text"]

if len(configuration) > 0:
    not_executed_commands = '\n'.join(configuration.keys())
    print(
        "\n"
        "Commands not executed:\n"
        f"{not_executed_commands}"
    )

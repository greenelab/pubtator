# Configuration Files

## File Description

| File | Description |
| --- | --- | 
| [pubtator central config](pubtator_central_config.json) | This is a configuration file for parsing Pubtator Central. |
| [pubtator config](pubtator_config.json) | This is a configuration file for parsing Pubtator (older version of Pubtator Central). |
| [tests config](tests_config.json) | This is a configuration file for testing the pubtator system. Feel free to ignore this file. |

## Usage

Each configuration file is in json format and contains parameters for each step within the pubtator pipeline. 
All files are organized by order of operation, which means the very first step occurs at the top and the subsequent step comes right afterwards.
Every step can be skipped, which allows one to continue the pipeline at any step one chooses. 
Please refer to [CONFIG.md](CONFIG.md) for more details on each pipeline step and their respective parameters.

Example config file:
```json
{
  "pipeline step 1":{
    "param1":"param1_value",
    "param2":"param2_value",
    "skip":false
    },
   "pipeline step 2":{
    "param1":"param1_value",
    "param2":"param2_value",
    "skip":false
    },
   "pipeline step 3":{
    "param1":"param1_value",
    "param2":"param2_value",
    "skip":false
    }
}
```

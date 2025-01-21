# Running a benchmark

## TL;DR -- Do everything for comparing two (or more) embedding models
```sh
pip install -r requirements.txt
python fill_database.py --model all-MiniLM-L6-v2 ./benchmark/Laurent\ initial\ benchmark/keyword_samples.json
python fill_database.py --model all-mpnet-base-v2 ./benchmark/Laurent\ initial\ benchmark/keyword_samples.json
python fill_database.py --model togethercomputer/m2-bert-80M-8k-retrieval@Together ./benchmark/Laurent\ initial\ benchmark/keyword_samples.json
python run_benchmark.py --models all-MiniLM-L6-v2,all-mpnet-base-v2,togethercomputer/m2-bert-80M-8k-retrieval@Together --nb_results 3 ./benchmark/Laurent\ initial\ benchmark/bench_definition.tsv report.html
rm -r ./chromadb/database
```

## Setup
```sh
pip install -r requirements.txt
```
installs the required Python ppackages.

## Fill the Chroma database with keywords
```sh
python fill_database.py --model togethercomputer/m2-bert-80M-8k-retrieval@Together --db_path ./chromadb/db --project my_project my_list.json
```
populates the database using a given embedding model with the keywords stored in the `my_list.json` file (see [below](#schema-of-the-keyword-json)), the data is stored under the project `my_project`.  
If the database does not exist before running the script, this one will create it.  
If the embedding model is not present on the computer, the script will download and install it.  
If an ID already exists for a given model and keyword type, the corresponding keyword and description will be replaced.  
(There is currently no way to remove a given keyword and/or description from the database.)

## Query the Chroma database
```sh
python query_database.py --model togethercomputer/m2-bert-80M-8k-retrieval@Together --db_path ./chromadb/db --project my_project --keyword_type "Outcome" --nb_results 5 "I have a saved receiving address"
```
looks for the `I have a saved receiving address` string in the keywords and descriptions of the Outcome keywords (in the project `my_project`) using embedding model `togethercomputer/m2-bert-80M-8k-retrieval` hosted by Together.

## Run a benchmark
```sh
python run_benchmark.py --models all-MiniLM-L6-v2,all-mpnet-base-v2,togethercomputer/m2-bert-80M-8k-retrieval@Together --db_path chromadb/db --project my_project --nb_results 3 ./benchmark/Laurent\ initial\ benchmark/bench_definition.tsv report.html
```
runs a benchmark.  
`benchmark/Laurent\ initial\ benchmark/bench_definition.tsv` is the benchmark definition. This one is a TSV (Tab Separated Value) file. The first line contains the headers, it is ignored. Each other line must contains a keyword type, a looked-up keyword, and the ID of the expected matching keyword (the matching being via the keyword itself or via its definition).  
`report.html` is the name of the HTML benchmark report that will be generated.

## Explore the Chroma database
```sh
python run_web_server.py --db_path chromadb/db --browser
```
displays the whole content of the database in the Browser.

## Delete the Chroma database
```sh
rm -r ./chromadb/database
```
deletes the Chroma database.

## Parameters
| parameter        | meaning                                                           | default value         |
| ---------------- | ----------------------------------------------------------------- | --------------------- |
| `--model`        | name of the embedding model (see [below](#usable-models))         | `all-MiniLM-L6-v2`    |
| `--models`       | comma-separated list of model names (see [below](#usable-models)) |                       |
| `--db_path`      | folder where is the ChromaDB database                             | `./chromadb/database` |
| `--project`      | name of the project                                               | `Common`              |
| `--keyword_type` | `Context`, `Action`, or `Outcome`                                 |                       |
| `--nb_results  ` | number of matches to return                                       | `3`                   |
| `--browser`      | open the Web Browser                                              |                       |

## Schema of the keyword JSON
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "keywords": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "type": {
            "type": "string",
            "enum": ["Context", "Action", "Outcome"]
          },
          "keyword": {
            "type": "string"
          },
          "description": {
            "type": "string"
          },
          "id": {
            "type": "string"
          }
        },
        "required": ["type", "keyword", "description", "id"],
        "additionalProperties": false
      }
    }
  },
  "required": ["keywords"],
  "additionalProperties": false
}
```

## Usable models
The name of a model is formatted as `model_name@host`, where `model_name` is the name of the model and `host` is the name of the embedding host.  
For local embedding models, simply use `model_name`.

| host        | model name                                                                                                   | environment variable defining the API key |
| ----------- | ------------------------------------------------------------------------------------------------------------ | ----------------------------------------- |
|             | all-MiniLM-L6-v2                                                                                             |                                           |
|             | all-mpnet-base-v2                                                                                            |                                           |
|             | … the list is [here](https://www.sbert.net/docs/sentence_transformer/pretrained_models.html#original-models) |                                           |
| Together    | togethercomputer/m2-bert-80M-8k-retrieval                                                                    | TOGETHER_API_KEY                          |
| Together    | togethercomputer/m2-bert-80M-32k-retrieval                                                                   | TOGETHER_API_KEY                          |
| Together    | … the list is [here](https://api.together.ai/models)                                                         | TOGETHER_API_KEY                          |
| Cohere      | embed-multilingual-v3.0                                                                                      | COHERE_API_KEY                            |
| Cohere      | embed-multilingual-light-v3.0                                                                                | COHERE_API_KEY                            |
| Cohere      | … the list is [here](https://api.together.ai/models)                                                         | COHERE_API_KEY                            |
| Mistral     | mistral-embed                                                                                                | MISTRAL_API_KEY                           |
| HuggingFace | sentence-transformers/all-MiniLM-L6-v2                                                                       | HUGGINGFACE_API_KEY                       |
| HuggingFace | sentence-transformers/all-mpnet-base-v2                                                                      | HUGGINGFACE_API_KEY                       |
| HuggingFace | … the list is [here](https://huggingface.co/models?filter=sentence-transformers)                             | HUGGINGFACE_API_KEY                       |

# Helpers

## Extraction of the keywords appearing in some feature files
You can use this if you want to create a keyword library from your existing feature files.
```sh
python keyword_extractor.py [--string_delimiter "'"] Gherkin\ samples/*.feature my_list.json
```
will create `my_list.json` which is the list of all keywords appearing in the `samples/*.feature` files.  
Keywords that only differ by integer values, float values, string values, or parameter names are merged (the longest one is kept).  
Use `--string_delimiter "'"` if the string values are delimited by single quotes (by default, they are delimited by double quotes).

## Extraction of the keywords appearing in a GitHub project
```sh
REPO=https://github.com/danascheider/tessitura-front-end.git
DIR=features
git clone --filter=blob:none --no-checkout --depth 1 --sparse $REPO
cd `basename -s .git $REPO`
git config set --global --append safe.directory `pwd`
git sparse-checkout set $DIR
git checkout

python ../keyword_extractor.py --string_delimiter "'"  features/*.feature ../my_list.json

git config unset --global --value `pwd` safe.directory
cd ..
rm -rf `basename -s .git $REPO`
```

# Running a benchmark

## TL;DR -- Do everything for comparing two (or more) embedding models
```sh
pip install -r requirements.txt
python fillDatabase.py --model all-MiniLM-L6-v2 --db_path ./chromadb/database ./benchmark/Laurent\ initial\ benchmark/keyword_samples.json
python fillDatabase.py --model all-mpnet-base-v2 --db_path ./chromadb/database ./benchmark/Laurent\ initial\ benchmark/keyword_samples.json
python runBenchmark.py --models all-MiniLM-L6-v2,all-mpnet-base-v2 --nb_results 3 ./benchmark/Laurent\ initial\ benchmark/bench_definition.tsv report.html
rm -r ./chromadb/database
```

## Setup
```sh
pip install -r requirements.txt
```
installs the required Python ppackages.

## Fill the Chroma database with keywords
```sh
python fillDatabase.py --model all-MiniLM-L6-v2 --db_path ./chromadb/database my_list.json
```
populates the database using a given embedding model with the keywords stored in the `my_list.json` file (see [below](#schema-of-the-keyword-json)).  
If the database does not exist before running the script, this one will create it.  
If the embedding model is not present on the computer, the script will download and install it.  
If an ID already exists for a given model and keyword type, the corresponding keyword and description will be replaced.  
(There is currently no way to remove a given keyword and/or description from the database.)

## Query the Chroma database
```sh
python queryDatabase.py --model all-MiniLM-L6-v2 --db_path ./chromadb/database --keyword_type "Outcome" --nb_results 5 "I have a saved receiving address"
```
looks for the `I have a saved receiving address` string in the keywords and descriptions of the Outcome keywords using embedding model `all-MiniLM-L6-v2`.

## Run a benchmark
```sh
python runBenchmark.py --models all-MiniLM-L6-v2,all-mpnet-base-v2 --db_path chromadb/database --nb_results 3 ./benchmark/Laurent\ initial\ benchmark/bench_definition.tsv report.html
```
runs a benchmark.  
`benchmark/Laurent\ initial\ benchmark/bench_definition.tsv` is the benchmark definition. This one is a TSV (Tab Separated Value) file. The first line contains the headers, it is ignored. Each other line must contains a keyword type, a looked-up keyword, and the ID of the expected matching keyword (the matching being via the keyword itself or via its definition).  
`report.html` is the name of the HTML benchmark report that will be generated.

## Navigate the Chroma database
```sh
python run_web_server.py --db_path chromadb/database --browser
```
displays the whole content of the database in the Browser.

## Delete the Chroma database
```sh
rm -r ./chromadb/database
```
deletes the Chroma database.

## Parameters
| parameter        | meaning                                                           |
| ---------------- | ----------------------------------------------------------------- |
| `--model`        | name of the embedding model (see [below](#usable-models))         |
| `--models`       | comma-separated list of model names (see [below](#usable-models)) |
| `--db_path`      | folder where is the ChromaDB database                             |
| `--keyword_type` | `Context`, `Action`, or `Outcome`                                 |
| `--nb_results  ` | number of matches to return                                       |

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
You can use the models listed [here](https://www.sbert.net/docs/sentence_transformer/pretrained_models.html#original-models).

# Helpers

## Extraction of the keywords appearing in some feature files
You can use this if you want to create a keyword library from your existing feature files.
```sh
python keywordExtractor.py [--string_delimiter "'"] Gherkin\ samples/*.feature my_list.json
```
will create `my_list.json` which is the list of all keywords appearing in the `samples/*.feature` files.  
Keywords that only differ by integer values, float values, string values, or parameter names are merged (the longest one is kept).  
Use `--string_delimiter "'"` if the string values are delimted by single quotes (by default, they are delimted by double quotes).

## Extraction of the keywords appearing in a GitHub project
```sh
REPO=https://github.com/danascheider/tessitura-front-end.git
DIR=features
git clone --filter=blob:none --no-checkout --depth 1 --sparse $REPO
cd `basename -s .git $REPO`
git config set --global --append safe.directory `pwd`
git sparse-checkout set $DIR
git checkout

python ../keywordExtractor.py --string_delimiter "'"  features/*.feature ../my_list.json

git config unset --global --value `pwd` safe.directory
cd ..
rm -rf `basename -s .git $REPO`
```

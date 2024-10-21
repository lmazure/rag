# Running a benchmark

## TL;DR -- Do everything for comparing two (or more) models
```sh
pip install -r requirements.txt
python fillDatabase.py --model all-MiniLM-L6-v2 --db_path ./chromadb/database benchmark/keyword_samples.json
python fillDatabase.py --model all-mpnet-base-v2 --db_path ./chromadb/database benchmark/keyword_samples.json
python runBenchmark.py --models all-MiniLM-L6-v2,all-mpnet-base-v2 --nb_results 3 benchmark/bench_definition.tsv report.html
rm -r chromadb/database
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
(There is currently no way to remove a given from the database.)

## Query the Chroma database
```sh
python queryDatabase.py --model all-MiniLM-L6-v2 --db_path ./chromadb/database --keyword_type "Outcome" --nb_results 5 "I have a saved receiving address"
```
looks for the `I have a saved receiving address` string in the keyword and decriptions of the Outcome ketywords using embedding model `all-MiniLM-L6-v2`.

## Run a benchmark
```sh
python runBenchmark.py --models all-MiniLM-L6-v2,all-mpnet-base-v2 --nb_results 3 benchmark/bench_definition.tsv report.html
```
runs a benchmark.  
`benchmark/bench_definition.tsv` is the branchmark definition. This one is a TSV (Tab Separated Value) file. THe first line contain the headers, it is ignored. Each other line must contains a keyword type, a looked-up keyword, and the ID of the exepcted matching keyword (the matching being via the keyword itself or via its definition).  
`report.html` is the name of the HTML benchmark report that will be generated.

## Dump content the Chroma database
```sh
python dumpDatabase.py --db_path chromadb/database
```
will display the whole content of the database.

## Delete the Chroma database
```sh
rm -r chromadb/database
```

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
python keywordExtractor.py Gkerkin\ samples/*.feature my_list.json
```
will create `my_list.json` which is the list of all keywords appearing in the `samples/*.feature` files.

# Todo
- `dumpDatabase.py` - the structure of the internal IDs (`foo-k` and `foo-d`) should be hidden
- JSON schema - keyword cannot be empty
- support other models
- `keywordExtractor.py` - test unicity of keywords
- `keywordExtractor.py` - management of incorrect feature files
- `keywordExtractor.py` - management of the datatable column names
- `keywordExtractor.py` - ☠ ⸘management of the parameters‽

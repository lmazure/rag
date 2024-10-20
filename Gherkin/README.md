# Running a benchmark

## Setup
```sh
pip install -r requirements.txt
```

## Fill the Chroma database with keywords
```sh
python fillDatabase.py --model all-MiniLM-L6-v2 --db_path ./chromadb/database my_list.json
```
populates the database with the keywords stored in the `my_list.json` file (see [below](#schema-of-the-keyword-json)).

## Query the Chroma database
```sh
python queryDatabase.py --model all-MiniLM-L6-v2 --db_path ./chromadb/database --keyword_type "Outcome" --nb_results 5 "I have a saved receiving address"
```

## Run a benchmark
```sh
python runBenchmark.py --models all-MiniLM-L6-v2,all-mpnet-base-v2 --nb_results 3 benchmark/bench_definition.tsv report.html
```
runs a beanchmark.  
`benchmark/bench_definition.tsv` is the branchmark definition, each line contains the looed-up keyword and the ID of the exepcted matching keyword, separatd by a tab.  
`report.html` is the name of the HTML benchmark report that will be generated.

## Dump content the Chroma database
```sh
python dumpDatabase.py --db_path chromadb/database
```

## Delete the Chroma database
```sh
rm -r chromadb/database
```

## Do everything for comparing two (or more) models
```sh
pip install -r requirements.txt
python fillDatabase.py --model all-MiniLM-L6-v2 --db_path ./chromadb/database benchmark/keyword_samples.json
python fillDatabase.py --model all-mpnet-base-v2 --db_path ./chromadb/database benchmark/keyword_samples.json
python runBenchmark.py --models all-MiniLM-L6-v2,all-mpnet-base-v2 --nb_results 3 benchmark/bench_definition.tsv report.html
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

- test unicity of keywords
- management of incorrect feature files
- management of the datatable column names
- ☠ ⸘management of the parameters‽

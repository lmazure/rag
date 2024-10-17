
## Setup
```sh
pip install -r requirements.txt
```

## Extraction of the keywords appearing in some feature files
```sh
python keywordExtractor.py my_list.json Gkerkin\ samples/*.feature
```
will create `my_list.json` which is the list of all keywords appearing in the `samples/*.feature` files.

## Fill the ChromaDB database with keywords
```sh
python fillDatabase.py --model all-MiniLM-L6-v2 --db_path ./chromadb/database my_list.json
```
populate the database with the keywords stored in the `my_list.json` file.

## query the CHromaDB database
```sh
python queryDatabase.py --model all-MiniLM-L6-v2 --db_path ./chromadb/database --keyword_type "Outcome" --nb_results 5 "I have a saved receiving address"
```


## todo
- manage description
- add IDs
- management of incorrect feature files

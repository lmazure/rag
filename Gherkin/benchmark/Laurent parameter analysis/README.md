load the data in Chroma
```sh
python fill_database.py --model all-MiniLM-L6-v2 --db_path ./chromadb/db --project angles benchmark/Laurent\ parameter\ analysis/keywords.json
python fill_database.py --model all-mpnet-base-v2 --db_path ./chromadb/db --project angles benchmark/Laurent\ parameter\ analysis/keywords.json
python fill_database.py --model all-distilroberta-v1 --db_path ./chromadb/db --project angles benchmark/Laurent\ parameter\ analysis/keywords.json
python fill_database.py --model all-MiniLM-L12-v2 --db_path ./chromadb/db --project angles benchmark/Laurent\ parameter\ analysis/keywords.json
```
run the benchmark
```sh
python run_benchmark.py --models all-MiniLM-L6-v2,all-mpnet-base-v2,all-distilroberta-v1,all-MiniLM-L12-v2 --db_path chromadb/db --project angles --nb_results 12 ./benchmark/Laurent\ parameter\ analysis/test.tsv report.html
```

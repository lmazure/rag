create benchmark/Laurent French benchmark/mistral.json
```bash
python keywordExtractor.py Gherkin\ samples/Mistral\ example\ *.feature mistral.json
```	

run benchmark
```bash
python fill_database.py --model all-MiniLM-L6-v2 --project Mistral --db_path ./chromadb/database benchmark/Laurent\ French\ benchmark/mistral.json
python fill_database.py --model all-mpnet-base-v2 --project Mistral --db_path ./chromadb/database benchmark/Laurent\ French\ benchmark/mistral.json
python run_benchmark.py --models all-MiniLM-L6-v2,all-mpnet-base-v2 --project Mistral --nb_results 3 ./benchmark/Laurent\ French\ benchmark/bench_definition.tsv report.html
```

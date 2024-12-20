create benchmark/Laurent French benchmark/mistral.json
```bash
python keywordExtractor.py Gherkin\ samples/Mistral\ example\ *.feature mistral.json
```	

run benchmark
```bash
python fillDatabase.py --model all-MiniLM-L6-v2 --db_path ./chromadb/database benchmark/Laurent\ French\ benchmark/mistral.json
python fillDatabase.py --model all-mpnet-base-v2 --db_path ./chromadb/database benchmark/Laurent\ French\ benchmark/mistral.json
python runBenchmark.py --models all-MiniLM-L6-v2,all-mpnet-base-v2 --nb_results 3 ./benchmark/Laurent\ French\ benchmark/bench_definition.tsv report.html
```

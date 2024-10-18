import argparse
import csv
from queryDatabase import extract_keywords

def process_file(file_path, models, db_path, nb_results, keyword_type):
    results = {}
    index = 0
    
    with open(file_path, 'r') as file:
        reader = csv.reader(file, delimiter='\t')
        for row in reader:
            
            keyword, expected_id = row
            keyword_results = {}
            
            for model in models:
                model_results = extract_keywords(db_path, model, keyword_type, keyword, nb_results)
                keyword_results[model] = { 'matches': model_results, 'success': expected_id in [result['id'] for result in model_results] }
            
            results[index] = {
                'keyword': keyword,
                'results': keyword_results
            }
            index += 1
    return results

def main():
    parser = argparse.ArgumentParser(description="Process keywords using multiple models and Chroma database.")
    parser.add_argument("--models", required=True, help="Comma-separated list of model names")
    parser.add_argument("--db_path", default="./chromadb/database", help="Path to the Chroma database (default: ./chromadb/database)")
    parser.add_argument("--nb_results", default=3, type=int, required=True, help="Number of matches to return (default: 3)")
    parser.add_argument("--keyword_type", required=True, choices=["Context", "Action", "Outcome"], help="Type of keyword")
    parser.add_argument("input_file", help="Path to the input file containing keywords and IDs")

    args = parser.parse_args()
    
    models = [model.strip() for model in args.models.split(',')]
    
    results = process_file(args.input_file, models, args.db_path, args.nb_results, args.keyword_type)
    
    # Print results
    for id, data in results.items():
        print(f"\nResults for ID: {id}, Keyword: {data['keyword']}")
        for model, model_results in data['results'].items():
            print(f"\n  Model: {model}")
            for result in model_results['matches']:
                print(f"    {result['id']}\t{result['keyword']}")
            print(f"    Success: {model_results['success']}")

if __name__ == "__main__":
    main()

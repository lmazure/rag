import argparse

import common
import vector_db

def main():
    parser = argparse.ArgumentParser(description="Query Chroma database for keyword matches.")
    parser.add_argument("--model", default="all-MiniLM-L6-v2", help="Embedding model to use (default: all-MiniLM-L6-v2)")
    parser.add_argument("--db_path", default="./chromadb/database", help="Path to the Chroma database (default: ./chromadb/database)")
    parser.add_argument("--project", default="Common", help="Name of the project (default: Common)")
    parser.add_argument("--nb_results", default=3, type=int, help="Number of matches to return (default: 3)")
    parser.add_argument("--keyword_type", required=True, choices=["Context", "Action", "Outcome"], help="Type of keyword")
    parser.add_argument("keyword", help="Keyword to query")
    
    args = parser.parse_args()

    model, host = common.parse_model_and_host(args.model)
    results = vector_db.search_keywords(args.db_path, host, model, args.project, args.keyword_type, args.keyword, args.nb_results)

    # Print results
    print(f"Top {len(results)} matches for '{args.keyword}' in {args.project} project in {args.keyword_type} category:")
    print("ID\tMatch\tKeyword\tKeyword distance\tDescription\tDescription distance")
    for result in results:
        print(f"{result['id']}\t{result['match']}\t{result['keyword']}\t{(result['keyword_distance']) if 'keyword_distance' in result else '-'}\t{result['description'] if 'description' in result else '-'}\t{(result['description_distance']) if 'description_distance' in result else '-'}")

if __name__ == "__main__":
    main()

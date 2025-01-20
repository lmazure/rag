import argparse
import json

import common
import model_db
import vector_db

def main():
    parser = argparse.ArgumentParser(description="Compute embedding vectors and store them in the Chroma database.")
    parser.add_argument("keyword_file", help="JSON file containing keywords")
    parser.add_argument("--model", default="all-MiniLM-L6-v2", help="Embedding model to use (default: all-MiniLM-L6-v2)")
    parser.add_argument("--db_path", default="./chromadb/database", help="Path to the Chroma database (default: ./chromadb/database)")
    parser.add_argument("--project", default="Common", help="Name of the project (default: Common)")
    args = parser.parse_args()
    model, host = common.parse_model_and_host(args.model)

    # Setup database
    model_db.setup_database(args.db_path)

    # Load keywords
    with open(args.keyword_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    vector_db.fill_database(args.db_path, model, host, args.project, data)

if __name__ == "__main__":
    main()

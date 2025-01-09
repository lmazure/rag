import argparse
import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
import json
import common

def main():
    parser = argparse.ArgumentParser(description="Compute embedding vectors and store them in the Chroma database.")
    parser.add_argument("keyword_file", help="JSON file containing keywords")
    parser.add_argument("--model", default="all-MiniLM-L6-v2", help="Embedding model to use (default: all-MiniLM-L6-v2)")
    parser.add_argument("--db_path", default="./chromadb/database", help="Path to the Chroma database (default: ./chromadb/database)")
    parser.add_argument("--project", default="Common", help="Name of the project (default: Common)")
    args = parser.parse_args()

    chroma_client = chromadb.PersistentClient(path=args.db_path, settings=Settings(anonymized_telemetry=False))
    
    collections = {
        "Context": chroma_client.get_or_create_collection(name=f"{common.get_collection_name(args.model, args.project, 'Context')}", \
                                                          embedding_function=SentenceTransformerEmbeddingFunction(model_name=args.model)),
        "Action": chroma_client.get_or_create_collection(name=f"{common.get_collection_name(args.model, args.project, 'Action')}"   , \
                                                         embedding_function=SentenceTransformerEmbeddingFunction(model_name=args.model)),
        "Outcome": chroma_client.get_or_create_collection(name=f"{common.get_collection_name(args.model, args.project, 'Outcome')}", \
                                                          embedding_function=SentenceTransformerEmbeddingFunction(model_name=args.model))
    }

    with open(args.keyword_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    keywords = data['keywords']
    for i, item in enumerate(keywords):
        collections[item['type']].upsert(documents=[item['keyword']], ids=[f"{item['id']}-k"])
        if len(item['description']):
            collections[item['type']].upsert(documents=[item['description']], ids=[f"{item['id']}-d"])

if __name__ == "__main__":
    main()

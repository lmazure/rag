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
    model, host = common.parse_model_and_host(args.model)

    chroma_client = chromadb.PersistentClient(path=args.db_path, settings=Settings(anonymized_telemetry=False))
    embedding_function =  common.build_embedding_function(host, model)

    with open(args.keyword_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    for type in ["Context", "Action", "Outcome"]:
        collection = chroma_client.get_or_create_collection(name=f"{common.get_collection_name(model, args.project, type)}", embedding_function=embedding_function)
        keywords = [item for item in data['keywords'] if item['type'] == type]
        if keywords != []:
            collection.upsert(documents=[item['keyword'] for item in keywords], ids=[f"{item['id']}-k" for item in keywords])
            documented_keywords = [item for item in keywords if len(item['description']) > 0]
            if documented_keywords != []:
                collection.upsert(documents=[item['description'] for item in documented_keywords], ids=[f"{item['id']}-d" for item in documented_keywords])

if __name__ == "__main__":
    main()

import argparse
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
import pprint

def main():
    parser = argparse.ArgumentParser(description="Query Chroma database for keyword matches.")
    parser.add_argument("--model", default="all-MiniLM-L6-v2", help="Embedding model to use (default: all-MiniLM-L6-v2)")
    parser.add_argument("--db_path", default="./chromadb/database", help="Path to the Chroma database (default: ./chromadb/database)")
    parser.add_argument("--nb_results", default=3, type=int, required=True, help="Number of matches to return (default: 3)")
    parser.add_argument("--keyword_type", required=True, choices=["Context", "Action", "Outcome"], help="Type of keyword")
    parser.add_argument("keyword", help="Keyword to query")
    
    args = parser.parse_args()

    # Initialize Chroma client
    chroma_client = chromadb.PersistentClient(path=args.db_path)

    # Get the appropriate collection
    collection_name = f"{args.model}-{args.keyword_type}"
    collection = chroma_client.get_collection(
        name=collection_name,
        embedding_function=SentenceTransformerEmbeddingFunction(model_name=args.model)
    )

    # Perform the query
    results = collection.query(
        query_texts=[args.keyword],
        n_results=args.nb_results
    )

    # Print results
    print(f"Top {args.nb_results} matches for '{args.keyword}' in {args.keyword_type} category:")
    for i in range(args.nb_results):
        print(f"{results['ids'][0][i]}\t{results['documents'][0][i]}")

if __name__ == "__main__":
    main()

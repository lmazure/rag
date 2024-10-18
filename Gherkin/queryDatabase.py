import argparse
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

def extract_keywords(db_path, model, keyword_type, keyword, nb_results):
    # Initialize Chroma client
    chroma_client = chromadb.PersistentClient(path=db_path)

    # Get the appropriate collection
    collection_name = f"{model}-{keyword_type}"
    collection = chroma_client.get_collection(
        name=collection_name,
        embedding_function=SentenceTransformerEmbeddingFunction(model_name=model)
    )

    # Perform the query
    results = collection.query(
        query_texts=[keyword],
        n_results=nb_results
    )

    print(results)
    return [{"id": results['ids'][0][i], "keyword": results['documents'][0][i]} for i in range(len(results['ids'][0]))]

def main():
    parser = argparse.ArgumentParser(description="Query Chroma database for keyword matches.")
    parser.add_argument("--model", default="all-MiniLM-L6-v2", help="Embedding model to use (default: all-MiniLM-L6-v2)")
    parser.add_argument("--db_path", default="./chromadb/database", help="Path to the Chroma database (default: ./chromadb/database)")
    parser.add_argument("--nb_results", default=3, type=int, required=True, help="Number of matches to return (default: 3)")
    parser.add_argument("--keyword_type", required=True, choices=["Context", "Action", "Outcome"], help="Type of keyword")
    parser.add_argument("keyword", help="Keyword to query")
    
    args = parser.parse_args()

    results = extract_keywords(args.db_path, args.model, args.keyword_type, args.keyword, args.nb_results)

    # Print results
    print(f"Top {len(results)} matches for '{args.keyword}' in {args.keyword_type} category:")
    for result in results:
        print(f"{result['id']}\t{result['keyword']}")

if __name__ == "__main__":
    main()

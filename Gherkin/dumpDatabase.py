import chromadb
import argparse

def dump_chromadb_collections(client):
    # Get all collection names
    collections = client.list_collections()
    print(collections, flush=True)
    for collection in collections:
        # Get the collection
        collection = client.get_collection(collection.name)
        
        # Get all documents in the collection
        results = collection.get(include=['documents'])
        
        print(f"\n=== {collection.name} ===")
        for doc_id, document in zip(results['ids'], results['documents']):
            print(f"{doc_id} {document}")

def main():

    parser = argparse.ArgumentParser(description="Dump the collections present in the Chroma database.")
    parser.add_argument("--db_path", default="./chromadb/database", help="Path to the Chroma database (default: ./chromadb/database)")
    args = parser.parse_args()

    client = chromadb.PersistentClient(path=args.db_path)

    dump_chromadb_collections(client)
    
if __name__ == "__main__":
    main()

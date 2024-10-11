import chromadb

database_location = "./chromadb/database"

chroma_client = chromadb.PersistentClient(path=database_location)

collection = chroma_client.get_or_create_collection(name="my_collection")

collection.upsert(
    documents=[
        "This is a document about pineapple",
        "This is a document about oranges"
    ],
    ids=["id1", "id2"]
)
results = collection.query(
    query_texts=["This is a query document about florida"], # Chroma will embed this for you
    n_results=2 # how many results to return
)
print(results)

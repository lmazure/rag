import chromadb
import json
import sys
import pprint

database_location = "./chromadb/database"

chroma_client = chromadb.PersistentClient(path=database_location)



def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py keyword_list.json")
        sys.exit(1)
    keyword_file = sys.argv[1]

    collections = {
        "Context": chroma_client.get_or_create_collection(name="Context"),
        "Action": chroma_client.get_or_create_collection(name="Action"),
        "Outcome": chroma_client.get_or_create_collection(name="Outcome")
    }

    with open(keyword_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    keywords = data['keywords']

    incr = 0
    for item in keywords:
          collections[item['type']].upsert(documents=[item['keyword']], ids=[f"id{incr:03d}"])
          incr += 1
 
    results = collections["Outcome"].query(
        query_texts=["I am on the command page"], # Chroma will embed this for you
        n_results=3 # how many results to return
    )
    pprint.pp(results, width=128)

if __name__ == "__main__":
    main()

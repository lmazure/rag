from together import Together
import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings
from chromadb.config import Settings
import uuid

# Set your Together AI API key

# Initialize ChromaDB client
client = chromadb.PersistentClient(path="./chromadb", settings=Settings(anonymized_telemetry=False))

# Create embedding function using Together AI's API
class MyCustomEmbeddingFunction(EmbeddingFunction[Documents]):
    def __init__(self, model: str):
        self.client = Together()
        self.model = model

    def __call__(self, input: Documents) -> Embeddings:
        """Embed the input documents."""
        embeddings = []
        response = self.client.embeddings.create(
            input=input,
            model=self.model
        )
        return [d.embedding for d in response.data]


# Create collection with the remote embedding function
embed = MyCustomEmbeddingFunction("togethercomputer/m2-bert-80M-8k-retrieval")
collection = client.create_collection(
    name="my_documents",
    embedding_function=embed
)

# Example documents
documents = [
    "The quick brown fox jumps over the lazy dog",
    "Machine learning is transforming the tech industry",
    "ChromaDB is a vector database for AI applications"
]

# Add documents to the collection
collection.add(
    documents=documents,
    ids=[str(uuid.uuid4()) for _ in range(len(documents))]
)

# Query the collection
query_text = "What is machine learning doing?"
results = collection.query(
    query_texts=[query_text],
    n_results=2
)

print("\nQuery:", query_text)
print("\nResults:")
for idx, doc in enumerate(results['documents'][0]):
    print(f"{idx + 1}. {doc}")

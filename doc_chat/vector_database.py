from typing import List
import chromadb
from chromadb.api.types import Metadata, QueryResult
from chromadb.config import Settings

from embedding_model_cohere import EmbeddingModelCohere
from embedding_model_gemini import EmbeddingModelGemini
from embedding_model_hugging_face import EmbeddingModelHuggingFace
from embedding_model_local import EmbeddingModelLocal
from embedding_model_mistral import EmbeddingModelMistral
from embedding_model_together import EmbeddingModelTogether

class VectorDatabase:
    def __init__(self, db_path: str):
        """
        Initialize the VectorDatabase with the given database path.

        Args:
            db_path (str): The path to the ChromaDB database.
        """
        self.db_path = db_path

    def build_embedding_function(self, host: str|None, model_name: str) -> None:
        """Build the embedding function."""
        embedding_classes = [
            EmbeddingModelCohere,
            EmbeddingModelGemini,
            EmbeddingModelHuggingFace,
            EmbeddingModelLocal,
            EmbeddingModelMistral,
            EmbeddingModelTogether
        ]
        
        for embedding_class in embedding_classes:
            if embedding_class.__name__ == f"EmbeddingModel{host}":
                return embedding_class.build_embedding_function(model_name)
        raise ValueError(f"Invalid embedding model host: {host}")

    def setup(self, model_name: str, host: str|None) -> None:
        """Initialize ChromaDB."""
        client = chromadb.PersistentClient(path=self.db_path, settings=Settings(anonymized_telemetry=False))
        embedding_function = self.build_embedding_function(host, model_name)
        self.collection = client.get_or_create_collection(name=f"docs_{model_name}", embedding_function=embedding_function)

    def add_chunks(self, chunks: List[str], metadatas: List[Metadata], ids: List[str]) -> None:
        """Add a chunk to the database."""
        self.collection.add(
            documents=chunks,
            metadatas=metadatas,
            ids=ids
            )

    def get_all_embeddings(self, embedding_set_id: int) -> List[str]:
        """Get all embeddings for a given embedding set."""
        return self.collection.get(
            where={"embedding_set_id": embedding_set_id}
        )

    def query(self, query: str, embedding_set_id: int) -> QueryResult:
        """Query the database."""
        results = self.collection.query(
            query_texts=[query],
            where={"embedding_set_id": embedding_set_id},
            n_results=5
        )
        return results

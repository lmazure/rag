from typing import List
import chromadb
from chromadb.api.types import Metadata, QueryResult
from chromadb.config import Settings

class VectorDatabase:
    def __init__(self, db_path: str):
        """
        Initialize the VectorDatabase with the given database path.

        Args:
            db_path (str): The path to the ChromaDB database.
        """
        self.db_path = db_path

    def setup(self) -> None:
        """Initialize ChromaDB."""
        client = chromadb.PersistentClient(path=self.db_path, settings=Settings(anonymized_telemetry=False))
        
        try:
            self.collection = client.get_collection("docs")
        except:
            self.collection = client.create_collection("docs")

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

    def query(self, query: str) -> QueryResult:
        """Query the database."""
        results = self.collection.query(
            query_texts=[query],
            n_results=10
        )
        return results

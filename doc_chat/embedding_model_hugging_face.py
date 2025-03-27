from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
from embedding_model import EmbeddingModel

class EmbeddingModelHuggingFace(EmbeddingModel):
    def __init__(self, model: str):
        super().__init__("HuggingFace", model)

    def build_embedding_function(self) -> EmbeddingFunction:
        return self.HuggingFaceEmbeddingFunction(self)

    class HuggingFaceEmbeddingFunction(EmbeddingFunction[Documents]):
        def __init__(self, embedding_model: EmbeddingModel):
            self.embedding_model = embedding_model

        def __call__(self, input: Documents) -> Embeddings:
            url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{self.embedding_model.get_model()}"
            token = self.embedding_model.get_envvar("HUGGINGFACE_API_KEY")
            payload = {
                "inputs": input
            }

            result = self.embedding_model.call_server(url, token, payload)
            return result

    @classmethod
    def get_available_models(cls) -> list[dict[str, str]]:
        return [ { "name": "sentence-transformers/all-MiniLM-L6-v2", "url": "https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2"}, \
            { "name": "sentence-transformers/all-mpnet-base-v2", "url": "https://huggingface.co/sentence-transformers/all-mpnet-base-v2"} ]

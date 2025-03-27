from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
from embedding_model import EmbeddingModel

class EmbeddingModelCohere(EmbeddingModel):
    def __init__(self, model: str):
        super().__init__("Cohere", model)

    def build_embedding_function(self) -> EmbeddingFunction:
        return self.CohereEmbeddingFunction(self)

    class CohereEmbeddingFunction(EmbeddingFunction[Documents]):
        def __init__(self, embedding_model: EmbeddingModel):
            self.embedding_model = embedding_model

        def __call__(self, input: Documents) -> Embeddings:
            # see https://docs.litellm.ai/docs/embedding/supported_embedding#cohere-embedding-models
            url = "https://api.cohere.ai/v1/embed"
            token = self.embedding_model.get_envvar("COHERE_API_KEY")
            payload = {
                "model": self.embedding_model.get_model(),
                "texts": input, 
                "input_type": "search_document"
                }

            result = self.embedding_model.call_server(url, token, payload)
            return result['embeddings']

    @classmethod
    def get_available_models(cls) -> list[dict[str, str]]:
        return [ { "name": "embed-multilingual-v3.0", "url": "https://docs.cohere.com/v2/docs/cohere-embed#multi-lingual-models"},
            { "name": "embed-multilingual-light-v3.0", "url": "https://docs.cohere.com/v2/docs/cohere-embed#multi-lingual-models"} ]

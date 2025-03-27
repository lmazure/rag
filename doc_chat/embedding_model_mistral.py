from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
from embedding_model import EmbeddingModel

class EmbeddingModelMistral(EmbeddingModel):
    def __init__(self, model: str):
        super().__init__("Mistral", model)

    def build_embedding_function(self) -> EmbeddingFunction:
        return self.MistralEmbeddingFunction(self)

    class MistralEmbeddingFunction(EmbeddingFunction[Documents]):
        def __init__(self, embedding_model: EmbeddingModel):
            self.embedding_model = embedding_model

        def __call__(self, input: Documents) -> Embeddings:
            url = "https://api.mistral.ai/v1/embeddings"
            token = self.embedding_model.get_envvar("MISTRAL_API_KEY")
            payload = {
                "model": self.embedding_model.get_model(),
                "input": input
            }

            result = self.embedding_model.call_server(url, token, payload)
            return [d['embedding'] for d in result['data']]

    @classmethod
    def get_available_models(cls) -> list[dict[str, str]]:
        return [ { "name": "mistral-embed", "url": "https://docs.mistral.ai/capabilities/embeddings/"} ]


from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
from embedding_model import EmbeddingModel

class EmbeddingModelGemini(EmbeddingModel):
    def __init__(self, model: str):
        super().__init__("Gemini", model)

    def build_embedding_function(self) -> EmbeddingFunction:
        return self.GeminiEmbeddingFunction(self)

    class GeminiEmbeddingFunction(EmbeddingFunction[Documents]):
        def __init__(self, embedding_model: EmbeddingModel):
            self.embedding_model = embedding_model

        def __call__(self, input: Documents) -> Embeddings:
            # see https://ai.google.dev/gemini-api/docs/embeddings#curl
            url = f"https://generativelanguage.googleapis.com/v1beta/{self.embedding_model.get_model()}:batchEmbedContents?key={self.embedding_model.get_envvar('GEMINI_API_KEY')}"
            payload = {
                "requests": [
                    {
                        "model": self.embedding_model.get_model(),
                        "content": {
                            "parts":[{"text": d} ]}
                    }
                for d in input]
            }

            result = self.embedding_model.call_server(url, None, payload)
            return [r['values'] for r in result['embeddings']]

    @classmethod
    def get_available_models(cls) -> list[dict[str, str]]:
        return [ { "name": "models/text-embedding-004", "url": "https://ai.google.dev/gemini-api/docs/models/gemini#text-embedding"},
            { "name": "models/embedding-001", "url": "https://ai.google.dev/gemini-api/docs/models/gemini#embedding-001"} ]

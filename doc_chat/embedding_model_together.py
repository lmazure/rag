from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
from embedding_model import EmbeddingModel


class EmbeddingModelTogether(EmbeddingModel):
    def __init__(self, model: str):
        super().__init__("Together", model)

    def build_embedding_function(self) -> EmbeddingFunction:
        return self.TogetherEmbeddingFunction(self)

    class TogetherEmbeddingFunction(EmbeddingFunction[Documents]):
        def __init__(self, embedding_model: EmbeddingModel):
            self.embedding_model = embedding_model

        def __call__(self, input: Documents) -> Embeddings:
            # see https://docs.together.ai/docs/embeddings-overview#generating-multiple-embeddings
            url = "https://api.together.xyz/v1/embeddings"
            token = self.embedding_model.get_envvar("TOGETHER_API_KEY")
            payload = {
                "model": self.embedding_model.get_model(),
                "input": input
            }

            result = self.embedding_model.call_server(url, token, payload)
            return [d['embedding'] for d in result['data']]

    @classmethod
    def get_available_models(cls) -> list[dict[str, str]]:
        return [ { "name": "togethercomputer/m2-bert-80M-32k-retrieval", "url": "https://api.together.ai/models/togethercomputer/m2-bert-80M-32k-retrieval"},
            { "name": "togethercomputer/m2-bert-80M-8k-retrieval", "url": "https://api.together.ai/models/togethercomputer/m2-bert-80M-8k-retrieval"},
            { "name": "togethercomputer/m2-bert-80M-2k-retrieval", "url": "https://api.together.ai/models/togethercomputer/m2-bert-80M-2k-retrieval"} ]

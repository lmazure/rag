from chromadb.api.types import EmbeddingFunction
from chromadb.utils.embedding_functions.sentence_transformer_embedding_function import SentenceTransformerEmbeddingFunction
from embedding_model import EmbeddingModel

class EmbeddingModelLocal(EmbeddingModel):

    def __init__(self, model: str):
        super().__init__("Local", model)

    def build_embedding_function(self) -> EmbeddingFunction:
        return SentenceTransformerEmbeddingFunction(model_name=self.get_model())

    @classmethod
    def get_available_models(cls) -> list[dict[str, str]]:
        return [ { "name": "multi-qa-mpnet-base-cos-v1", "url": "https://huggingface.co/sentence-transformers/multi-qa-mpnet-base-cos-v1"},
            { "name": "distiluse-base-multilingual-cased-v1", "url": "https://huggingface.co/sentence-transformers/distiluse-base-multilingual-cased-v1"},
            { "name": "distiluse-base-multilingual-cased-v2", "url": "https://huggingface.co/sentence-transformers/distiluse-base-multilingual-cased-v2"},
            { "name": "paraphrase-multilingual-MiniLM-L12-v2", "url": "https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"},
            { "name": "paraphrase-multilingual-mpnet-base-v2", "url": "https://huggingface.co/sentence-transformers/paraphrase-multilingual-mpnet-base-v2"}]

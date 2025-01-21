import requests
import json
import os

from chromadb import Documents, EmbeddingFunction, Embeddings
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

def get_envvar(name: str) -> str:
    val = os.getenv(name)
    if val is None:
        raise Exception(f"Environment variable {name} is not set")
    return val.strip()

def call_server(url: str, token: str, payload: dict[str, str]) -> dict[str, str]:

    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        error_message = response.text
        print(url + "\nreturned error\n" + error_message, flush=True)
        raise Exception("Model failed") from e
    except Exception as e:
        print(url + "\nfailed with exception\n" + str(e), flush=True)
        raise Exception("An error occurred") from e
    txt = response.text
    jsonz = {}
    try:
        jsonz = json.loads(txt)
    except BaseException as e:
        print(f"Error while trying to extract JSON\n{e}\nThe API answer is\n{txt}", flush=True)
        raise Exception(f"Error while trying to extract JSON from \"{txt}\", problem is: " + str(e)) from e
    return jsonz

class CohereEmbeddingFunction(EmbeddingFunction[Documents]):
    def __init__(self, model: str):
        self.model = model

    def __call__(self, input: Documents) -> Embeddings:
        # see https://docs.litellm.ai/docs/embedding/supported_embedding#cohere-embedding-models
        url = "https://api.cohere.ai/v1/embed"
        token = get_envvar("COHERE_API_KEY")
        payload = {
             "model": self.model,
             "texts": input, 
             "input_type": "search_document"
            }

        result = call_server(url, token, payload)
        return result['embeddings']

class TogetherEmbeddingFunction(EmbeddingFunction[Documents]):
    def __init__(self, model: str):
        self.model = model

    def __call__(self, input: Documents) -> Embeddings:
        # see https://docs.together.ai/docs/embeddings-overview#generating-multiple-embeddings
        url = "https://api.together.xyz/v1/embeddings"
        token = get_envvar("TOGETHER_API_KEY")
        payload = {
             "model": self.model,
             "input": input
            }

        result = call_server(url, token, payload)
        return [d['embedding'] for d in result['data']]

class MistralEmbeddingFunction(EmbeddingFunction[Documents]):
    def __init__(self, model: str):
        self.model = model

    def __call__(self, input: Documents) -> Embeddings:
        url = "https://api.mistral.ai/v1/embeddings"
        token = get_envvar("MISTRAL_API_KEY")
        payload = {
             "model": self.model,
             "input": input
            }

        result = call_server(url, token, payload)
        return [d['embedding'] for d in result['data']]

class HuggingFaceEmbeddingFunction(EmbeddingFunction[Documents]):
    def __init__(self, model: str):
        self.model = model

    def __call__(self, input: Documents) -> Embeddings:
        url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{self.model}"
        token = get_envvar("HUGGINGFACE_API_KEY")
        payload = {
             "inputs": input
            }

        result = call_server(url, token, payload)
        return result

def build_embedding_function(host: str, model: str) -> SentenceTransformerEmbeddingFunction:
    if (host == None) or (host == ''):
        return SentenceTransformerEmbeddingFunction(model_name=model)
    if host == "Cohere":
        return CohereEmbeddingFunction(model)
    if host == "Together":
        return TogetherEmbeddingFunction(model)
    if host == "Mistral":
        return MistralEmbeddingFunction(model)
    if host == "HuggingFace":
        return HuggingFaceEmbeddingFunction(model)
    raise ValueError(f"Unknown host ({host})")

from os import getenv
import re
import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings
from chromadb.config import Settings
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
import requests
import json

### parse model@host

def parse_model_and_host(model_and_host: str
                         ) -> tuple[str, str]:
    """
    Parse a string of the form "model@host" and return a tuple of (model, host).
    If "@" is absent, the host is None.
    """
    parts = model_and_host.split('@')
    if len(parts) == 1:
        return parts[0], None
    return parts[0], parts[1]

### management of collection names

def get_keyword_type(collection_name: str) -> str:
    """
    Return the keyword typefrom a collection name.
    For example, if the collection name is "model-my_project-Outcome", the keyword type is "Outcome".
    """
    return collection_name.split('-')[-1]

def get_project_name(collection_name: str) -> str:
    """
    Return the project name from a collection name.
    For example, if the collection name is "model-my_project-Outcome", the project name is "my_project".
    """
    return collection_name.split('-')[-2]

def get_host(collection_name: str) -> str:
    """
    Return the host of the model from a collection name.
    For example, if the collection name is "model-my_project-Outcome", the host is "my_project".
    """
    host = collection_name.split('-')[-3]
    if host:
        return host
    return None

def get_model(collection_name: str) -> str:
    """
    Return the model name from a collection name.
    For example, if the collection name is "model-my_project-Outcome", the model name is "model".
    """
    model_name = '-'.join(collection_name.split('-')[:-3])
    return model_name.replace("tc_--_","togethercomputer/")

def get_collection_name(model: str, host: str, project: str, keyword_type: str) -> str:
    """
    Return the collection name given a model, a host, a project, and a keyword type.
    For example, if the model is "model", the host is "Together", the project is "my_project", and the keyword type is "Outcome",
    the collection name is "model-Together-my_project-Outcome".
    """
    model_name = model.replace("togethercomputer/","tc_--_")
    if not re.match("^[-a-zA-Z0-9_]*$", model_name):
        raise ValueError(f"Error: Model name ({model_name}) can only contain characters, digits, dash, or underscores.")
    if host and not re.match("^[a-zA-Z]*$", host):
        raise ValueError(f"Error: Host ({host}) can only contain characters.")
    if not re.match("^[a-zA-Z0-9_]*$", project):
        raise ValueError(f"Error: Project name ({project}) can only contain characters, digits, or underscores.")
    if keyword_type not in ["Context", "Action", "Outcome"]:
        raise ValueError(f"Error: Keyword type ({keyword_type}) can only be 'Context', 'Action', or 'Outcome'.")
    return f"{model_name}-{host or ''}-{project}-{keyword_type}"



#### management of ids

def get_document_type(internal_id: str) -> str:
    """
    Return the type of a Chroma document given its internal id.
    The internal id is a string that can be decomposed into its external id; a dash, and a suffix that represents the type of document.
    Currently, the type of document can be either 'keyword' or 'description'.
    Args:
        internal_id: The internal id of the document.
    Returns:
        The type of document.
    Raises:
        ValueError: If the type of document is unknown.
    """
    type = internal_id.split('-')[-1]
    if type == 'k':
        return 'keyword'
    elif type == 'd':
        return 'description'
    else:
        raise ValueError("Unknown document type")

def get_external_id(internal_id: str) -> str:
    """
    Return the external id of keyword given its internal id or the internal id of its description.
    Args:
        internal_id: The internal id of the Chroma document.
    Returns:
        The external id of the keyword.
    """
    return '-'.join(internal_id.split('-')[:-1])

def get_internal_id_of_description(internal_keyword_id: str) -> str:
    """
    Get the internal id of a keyword description given the internal id of a keyword.
    
    Args:
        internal_keyword_id: The internal id of the keyword.
        
    Returns:
        The internal id of its description.
        
    Raises:
        ValueError: If the provided id is not of a keyword.
    """
    if get_document_type(internal_keyword_id) != 'keyword':
        raise ValueError("Not id of a keyword")
    return f"{get_external_id(internal_keyword_id)}-d"

def get_internal_id_of_keyword(internal_description_id: str) -> str:
    """
    Get the internal id of a keyword given the internal id of its description.
    
    Args:
        internal_description_id: The internal id of the description.
        
    Returns:
        The internal id of the keyword.
        
    Raises:
        ValueError: If the provided id is not of a description.
    """
    if get_document_type(internal_description_id) != 'description':
        raise ValueError("Not id of a description")
    return f"{get_external_id(internal_description_id)}-k"


### database queries

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

class TogetherEmbeddingFunction(EmbeddingFunction[Documents]):
    def __init__(self, model: str):
        self.model = model

    def __call__(self, input: Documents) -> Embeddings:
        url = "https://api.together.xyz/v1/embeddings"
        token = getenv("TOGETHER_API_KEY")
        payload = {
             "model": self.model,
             "input": input
            }

        result = call_server(url, token, payload)
        return [d['embedding'] for d in result['data']]

def build_embedding_function(host: str, model: str) -> SentenceTransformerEmbeddingFunction:
    if host == None:
        return SentenceTransformerEmbeddingFunction(model_name=model)
    if host == "Together":
        return TogetherEmbeddingFunction(model)
    raise ValueError(f"Unknown host ({host})")


def search_keywords(db_path: str, host: str, model: str, project: str, keyword_type: str, keyword: str, nb_results:int) -> list[dict[str, str]]:
    """
    Extract the nearest neighbours of a keyword from a Chroma database.

    Args:
        db_path: The path to the Chroma database.
        host: The host of the model.
        model: The name of the model.
        project: The name of the project.
        keyword_type: The type of keyword to extract.
        keyword: The keyword to search for.
        nb_results: The number of results to return.

    Returns:
        A list of dictionaries with the following keys:
            - id: The external id of the matching keyword.
            - match: What is matching the searched keyword ('keyword' or 'description').
            - keyword: The text of the matching keyword.
            - description: The description of the matching keyword. Absent if the keyword has no description.
            - keyword_distance: (May be missing if description matches) the distance between the matching keyword and the searched keyword.
            - description_distance: (May be missing if keyword matches) the distance between the description of the matching keyword and the searched keyword.

    Raises:
        ValueError: If the model and/or project do not exist in the database.
    """
    # Initialize Chroma client
    chroma_client = chromadb.PersistentClient(path=db_path, settings=Settings(anonymized_telemetry=False))

    # Get the appropriate collection
    collection_name = f"{get_collection_name(model, host, project, keyword_type)}"

    embedding_function = build_embedding_function(host, model)
    try:
        collection = chroma_client.get_collection(
            name=collection_name,
            embedding_function=embedding_function
        )
    except chromadb.errors.InvalidCollectionException as e:
        raise ValueError(f"Error: Model {model} and/or project {project} do not exist in database {db_path}.") from e

    documents = collection.get(include=['documents'])

    # Perform the search query
    search_results = collection.query(
        query_texts=[keyword],
        n_results=nb_results
    )

    data = []
    result_ids = search_results['ids'][0]
    result_docs = search_results['documents'][0]
    result_dists = search_results['distances'][0]
    for i in range(len(result_ids)):
        if get_document_type(result_ids[i]) == 'keyword':
            d = { 'id': get_external_id(result_ids[i]), 'match': 'keyword', 'keyword': result_docs[i], 'keyword_distance': result_dists[i]}
            description_id = get_internal_id_of_description(result_ids[i])
            if description_id in documents['ids']:
                d['description'] = documents['documents'][documents['ids'].index(description_id)]
                if description_id in result_ids:
                    d['description_distance'] = result_dists[result_ids.index(description_id)]
        else:
            d = { 'id': get_external_id(result_ids[i]), 'match': 'description', 'description': result_docs[i], 'description_distance': result_dists[i]}
            keyword_id = get_internal_id_of_keyword(result_ids[i])
            d['keyword'] = documents['documents'][documents['ids'].index(keyword_id)]
            if keyword_id in result_ids:
                d['keyword_distance'] = result_dists[result_ids.index(keyword_id)]
        data.append(d)
    return data

import re
import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
import common

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

def get_model(collection_name: str) -> str:
    """
    Return the model name from a collection name.
    For example, if the collection name is "model-my_project-Outcome", the model name is "model".
    """
    return '-'.join(collection_name.split('-')[:-2])

def get_collection_name(model_name: str, project_name: str, keyword_type: str) -> str:
    """
    Return the collection name given a model name, a project name, and a keyword type.
    For example, if the model name is "model", the project name is "my_project", and the keyword type is "Outcome",
    the collection name is "model-my_project-Outcome".
    """
    if not re.match("^[a-zA-Z0-9_]*$", project_name):
        raise ValueError("Error: Project name can only contain characters, digits, or underscores.")
    if keyword_type not in ["Context", "Action", "Outcome"]:
        raise ValueError("Error: Keyword type can only be 'Context', 'Action', or 'Outcome'.")
    return f"{model_name}-{project_name}-{keyword_type}"



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

def extract_keywords(db_path: str, model: str, project: str, keyword_type: str, keyword: str, nb_results:int) -> list[dict[str, str]]:
    """
    Extract the nearest neighbours of a keyword from a Chroma database.

    Args:
        db_path: The path to the Chroma database.
        model: The name of the model to use for the extraction.
        project: The name of the project to use for the extraction.
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
    collection_name = f"{common.get_collection_name(model, project, keyword_type)}"
    try:
        collection = chroma_client.get_collection(
            name=collection_name,
            embedding_function=SentenceTransformerEmbeddingFunction(model_name=model)
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
    for i in range(len(search_results['ids'][0])):
        if common.get_document_type(search_results['ids'][0][i]) == 'keyword':
            d = { 'id': common.get_external_id(search_results['ids'][0][i]), 'match': 'keyword', 'keyword': search_results['documents'][0][i], 'keyword_distance': search_results['distances'][0][i]}
            description_id = common.get_internal_id_of_description(search_results['ids'][0][i])
            if description_id in documents['ids']:
                d['description'] = documents['documents'][documents['ids'].index(description_id)]
                if description_id in search_results['ids'][0]:
                    d['description_distance'] = search_results['distances'][0][search_results['ids'][0].index(description_id)]
        else:
            d = { 'id': common.get_external_id(search_results['ids'][0][i]), 'match': 'description', 'description': search_results['documents'][0][i], 'description_distance': search_results['distances'][0][i]}
            keyword_id = common.get_internal_id_of_keyword(search_results['ids'][0][i])
            d['keyword'] = documents['documents'][documents['ids'].index(keyword_id)]
            if keyword_id in search_results['ids'][0]:
                d['keyword_distance'] = search_results['distances'][0][search_results['ids'][0].index(keyword_id)]
        data.append(d)
    return data

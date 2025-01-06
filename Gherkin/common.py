import re

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

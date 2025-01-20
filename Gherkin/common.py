import re

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
    For example, if the collection name is "123-my_project-Outcome", the keyword type is "Outcome".
    """
    return collection_name.split('-')[-1]

def get_project_name(collection_name: str) -> str:
    """
    Return the project name from a collection name.
    For example, if the collection name is "123-my_project-Outcome", the project name is "my_project".
    """
    return collection_name.split('-')[-2]

def get_model_id(collection_name: str) -> int:
    """
    Return the model name from a collection name.
    For example, if the collection name is "123-my_project-Outcome", the model id is 123.
    """
    return int(collection_name.split('-')[0])

def get_collection_name(model_id: int, project: str, keyword_type: str) -> str:
    """
    Return the collection name given a model id, a project, and a keyword type.
    For example, if the model_id is 123, the project is "my_project", and the keyword type is "Outcome",
    the collection name is "123-my_project-Outcome".
    """
    if not re.match("^[a-zA-Z0-9_]*$", project):
        raise ValueError(f"Error: Project name ({project}) can only contain characters, digits, or underscores.")
    if keyword_type not in ["Context", "Action", "Outcome"]:
        raise ValueError(f"Error: Keyword type ({keyword_type}) can only be 'Context', 'Action', or 'Outcome'.")
    return f"{model_id}-{project}-{keyword_type}"



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


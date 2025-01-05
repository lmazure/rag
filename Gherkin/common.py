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
    return f"{model_name}-{project_name}-{keyword_type}"

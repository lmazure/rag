import chromadb
from chromadb.api.types import IncludeEnum
from chromadb.config import Settings

import common
import model_db
import common_embed

def fill_database(db_path: str, model: str, host: str|None, project: str, data: dict) -> None:
    """
    Fill a Chroma database with keywords and their descriptions.

    Args:
        db_path: The path to the Chroma database.
        model: The name of the model.
        host: The host of the model.
        project: The name of the project.
        data: The data to write to the database, which should contain a 'keywords' key with a list of
            dictionaries containing the following keys:
                id (str): The ID of the keyword.
                type (str): The type of the keyword (Context, Action, or Outcome).
                keyword (str): The keyword itself.
                description (str): The description of the keyword (optional).

    Returns:
        None
    """
    # Initialize Chroma client
    chroma_client = chromadb.PersistentClient(path=db_path, settings=Settings(anonymized_telemetry=False))
    embedding_function = common_embed.build_embedding_function(host, model)

    model_id = model_db.get_model_id(db_path, model, host)
    if not model_id:
        model_id = model_db.add_model_and_host(db_path, model, host)

    for type in ["Context", "Action", "Outcome"]:
        keywords = [item for item in data['keywords'] if item['type'] == type]
        if keywords != []:
            collection = chroma_client.get_or_create_collection(name=f"{common.get_collection_name(model_id, project, type)}", embedding_function=embedding_function)
            collection.upsert(documents=[item['keyword'] for item in keywords], ids=[f"{item['id']}-k" for item in keywords])
            documented_keywords = [item for item in keywords if len(item['description']) > 0]
            if documented_keywords != []:
                collection.upsert(documents=[item['description'] for item in documented_keywords], ids=[f"{item['id']}-d" for item in documented_keywords])

    return

def search_keywords(db_path: str, host: str|None, model: str, project: str, keyword_type: str, keyword: str, nb_results:int) -> list[dict[str, str]]:
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

    # Extract the model id
    model_id = model_db.get_model_id(db_path, model, host)
    if not model_id:
        raise ValueError(f"Model {model} at host {host} do not exist in SQLite database {db_path}.")

    # Initialize Chroma client
    chroma_client = chromadb.PersistentClient(path=db_path, settings=Settings(anonymized_telemetry=False))

    # Get the appropriate embedding function
    embedding_function = common_embed.build_embedding_function(host, model)

    # Get the appropriate collection
    collection_name = f"{common.get_collection_name(model_id, project, keyword_type)}"
    try:
        collection = chroma_client.get_collection(
            name=collection_name,
            embedding_function=embedding_function
        )
    except ValueError as e:
        raise ValueError(f"Error: Model {model} and/or project {project} do not exist in Chroma database {db_path}.") from e

    documents = collection.get(include=[IncludeEnum.documents])
    assert documents['documents'] is not None

    # Perform the search query
    search_results = collection.query(
        query_texts=[keyword],
        n_results=nb_results
    )
    assert search_results['ids'] is not None
    assert search_results['documents'] is not None
    assert search_results['distances'] is not None

    # Process the search results
    data = []
    result_ids = search_results['ids'][0]
    result_docs = search_results['documents'][0]
    result_dists = search_results['distances'][0]
    for i in range(len(result_ids)):
        if common.get_document_type(result_ids[i]) == 'keyword':
            d = { 'id': common.get_external_id(result_ids[i]), 'match': 'keyword', 'keyword': result_docs[i], 'keyword_distance': result_dists[i]}
            description_id = common.get_internal_id_of_description(result_ids[i])
            if description_id in documents['ids']:
                d['description'] = documents['documents'][documents['ids'].index(description_id)]
                if description_id in result_ids:
                    d['description_distance'] = result_dists[result_ids.index(description_id)]
        else:
            d = { 'id': common.get_external_id(result_ids[i]), 'match': 'description', 'description': result_docs[i], 'description_distance': result_dists[i]}
            keyword_id = common.get_internal_id_of_keyword(result_ids[i])
            d['keyword'] = documents['documents'][documents['ids'].index(keyword_id)]
            if keyword_id in result_ids:
                d['keyword_distance'] = result_dists[result_ids.index(keyword_id)]
        data.append(d)

    return data

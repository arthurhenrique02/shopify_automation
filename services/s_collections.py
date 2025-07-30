from services.graphql.admin_api import graphql_request
from services.graphql.queries import (
    ADD_PRODUCT_COLLECTION_QUERY,
    CREATE_COLLECTION_QUERY,
    PUBLISH_COLLECTION_QUERY,
)


def create_collection(store_url: str, access_token: str, title: str) -> str:
    """
    Creates a collection in the Shopify store.
    Args:
        store_url (str): The URL of the Shopify store.
        access_token (str): The access token for the Shopify store.
        title (str): The title of the collection.
    Returns:
        str: The ID of the created collection.
    """
    if not store_url or not access_token or not title:
        raise ValueError("Shop URL, access token, and title must be provided.")

    data = graphql_request(
        store_url, access_token, CREATE_COLLECTION_QUERY, {"input": {"title": title}}
    )
    return data["data"]["collectionCreate"]["collection"]["id"]


def publish_collection(
    store_url: str, access_token: str, collection_id: str, publication_id: str
):
    data = graphql_request(
        store_url,
        access_token,
        PUBLISH_COLLECTION_QUERY,
        {
            "input": {
                "id": collection_id,
                "collectionPublications": {"publicationId": publication_id},
            }
        },
    )
    return data["data"]["collectionPublish"]["collection"]["id"]


def add_product_to_collection(
    store_url: str, access_token: str, product_id, collection_id
):
    graphql_request(
        store_url,
        access_token,
        ADD_PRODUCT_COLLECTION_QUERY,
        {"collectionId": collection_id, "productIds": [product_id]},
    )


def upload_collections(
    store_url: str, access_token: str, collections: list[dict]
) -> list[str]:
    """
    Uploads a list of collections to the Shopify store.
    Args:
        store_url (str): The url of the Shopify store.
        access_token (str): The access token for the Shopify store.
        collections (list[dict]): A list of collections to upload.
    Returns:
        list[str]: A list of collection IDs that were successfully created.
    """
    collections_id = []
    for collection in collections:
        title = collection.get("name")
        if not title:
            print("Collection title is required.")
            continue

        collection_id = create_collection(store_url, access_token, title)

        if not collection_id:
            print(f"Failed to create collection '{title}'.")
            continue

        collections_id.append(collection_id)
        print(f"Collection '{title}' created with ID: {collection_id}")

    return collections_id


def publish_collections(
    store_url: str, access_token: str, collection_ids: list[str], publication_id: str
) -> list[str]:
    """
    Publishes a list of collections in the Shopify store.
    Args:
        store_url (str): The URL of the Shopify store.
        access_token (str): The access token for the Shopify store.
        collection_ids (list[str]): A list of collection IDs to publish.
        publication_id (str): The ID of the publication to publish the collections to.
    Returns:
        list[str]: A list of published collection IDs.
    """
    published_collection_ids = []
    for collection_id in collection_ids:
        published_id = publish_collection(
            store_url, access_token, collection_id, publication_id
        )

        if not published_id:
            print(f"Failed to publish collection with ID {collection_id}.")
            continue
        published_collection_ids.append(published_id)
        print(f"Collection with ID {collection_id} published successfully.")

    return published_collection_ids

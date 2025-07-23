from services.graphql.admin_api import graphql_request
from services.graphql.queries import (
    ADD_PRODUCT_COLLECTION_QUERY,
    CREATE_COLLECTION_QUERY,
    PUBLISH_COLLECTION_QUERY,
)


def create_collection(title: str) -> str:
    data = graphql_request(CREATE_COLLECTION_QUERY, {"input": {"title": title}})
    return data["data"]["collectionCreate"]["collection"]["id"]


def publish_collection(collection_id: str, publication_id: str):
    data = graphql_request(
        PUBLISH_COLLECTION_QUERY,
        {"collectionId": collection_id, "publicationId": publication_id},
    )
    return data["data"]["collectionPublish"]["collection"]["id"]


def add_product_to_collection(product_id, collection_id):
    graphql_request(
        ADD_PRODUCT_COLLECTION_QUERY,
        {"collectionId": collection_id, "productIds": [product_id]},
    )

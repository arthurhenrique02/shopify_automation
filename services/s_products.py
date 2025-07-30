import csv

from services.graphql.admin_api import graphql_request
from services.graphql.queries import (
    CREATE_PRODUCT_MEDIA_QUERY,
    CREATE_PRODUCT_QUERY,
    CREATE_VARIANT_QUERY,
    PUBLISH_PRODUCT_QUERY,
)


def upload_product(row):
    title = row["Title"]
    body_html = row["Body (HTML)"]
    vendor = row["Vendor"]
    product_type = row["Type"]
    tags = row["Tags"].split(",") if row["Tags"] else []
    options = []

    # Handle options (like Cor, Tamanho)
    if row["Option1 Name"]:
        options.append(
            {"name": row["Option1 Name"], "values": {"name": row["Option1 Value"]}}
        )
    if row["Option2 Name"]:
        options.append(
            {"name": row["Option2 Name"], "values": {"name": row["Option2 Value"]}}
        )
    if row["Option3 Name"]:
        options.append(
            {"name": row["Option3 Name"], "values": {"name": row["Option3 Value"]}}
        )

    # Prepare variant
    variant = {
        "sku": row["Variant SKU"],
        "price": row["Variant Price"],
        "requiresShipping": row["Variant Requires Shipping"].lower() == "true",
        "taxable": row["Variant Taxable"].lower() == "true",
        "inventoryManagement": row["Variant Inventory Tracker"] or None,
        "inventoryPolicy": row["Variant Inventory Policy"] or "continue",
        "fulfillmentService": row["Variant Fulfillment Service"] or "manual",
        "weight": float(row["Variant Grams"] or 0) / 1000.0,
        "weightUnit": row["Variant Weight Unit"] or "kg",
    }

    # Build product input for GraphQL
    product_input = {
        "title": title,
        "descriptionHtml": body_html,
        "vendor": vendor,
        "productType": product_type,
        "tags": tags,
        "productOptions": options,
    }
    product_media = []

    # Add image
    if row["Image Src"]:
        product_media.append(
            {"originalSource": row["Image Src"], "mediaContentType": "IMAGE"}
        )

        # Variant image
        # TODO ADD VARIANT IMAGE IN PRODUCT VARIANT
        if row["Variant Image"]:
            product_media.append(
                {
                    "originalSource": row["Variant Image"],
                    "mediaContentType": "IMAGE",
                }
            )

    # GraphQL mutation
    query = CREATE_PRODUCT_QUERY
    result = graphql_request(query, {"product": product_input})

    # === create media ===
    media_query = CREATE_PRODUCT_MEDIA_QUERY
    product_id = result["data"]["productCreate"]["product"]["id"]

    if product_media:
        result_media = graphql_request(
            media_query,
            {
                "media": product_media,
                "productId": product_id,
            },
        )

    # ==== create variant ====
    variant_query = CREATE_VARIANT_QUERY

    variant_result = graphql_request(
        variant_query,
        {
            "productId": product_id,
            "variant": [variant],
        },
    )

    return result["data"]["productCreate"]


def upload_products_from_csv(csv_file):
    products = []
    with open(csv_file, encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            product = upload_product(row)
            products.append(product)

    return products


def publish_product(
    store_url: str, access_token: str, product_id: str, publication_id: str
):
    """
    Publishes a product to the specified publication.
    Args:
        store_url (str): The URL of the Shopify store.
        access_token (str): The access token for the Shopify store.
        product_id (str): The ID of the product to publish.
        publication_id (str): The ID of the publication to publish to.
    Returns:
        str: The ID of the published product.
    """
    data = graphql_request(
        store_url,
        access_token,
        PUBLISH_PRODUCT_QUERY,
        {"productId": product_id, "publicationId": publication_id},
    )
    return data["data"]["productPublish"]["product"]["id"]


def publish_products(
    store_url: str, access_token: str, product_ids: list[str], publication_id: str
):
    """
    Publishes multiple products to the specified publication.
    Args:
        store_url (str): The URL of the Shopify store.
        access_token (str): The access token for the Shopify store.
        product_ids (list[str]): A list of product IDs to publish.
        publication_id (str): The ID of the publication to publish to.
    Returns:
        list[str]: A list of IDs of the published products.
    """
    published_product_ids = []
    for product_id in product_ids:
        published_product_id = publish_product(
            store_url, access_token, product_id, publication_id
        )
        published_product_ids.append(published_product_id)
    return published_product_ids

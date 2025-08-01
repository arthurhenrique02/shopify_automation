import pandas as pd
from pandas.core.series import Series

from services.graphql.admin_api import graphql_request
from services.graphql.queries import (
    CREATE_PRODUCT_MEDIA_QUERY,
    CREATE_PRODUCT_QUERY,
    PUBLISH_PRODUCT_QUERY,
)


def upload_product(store_url: str, access_token: str, row: Series) -> dict:
    options = []
    for i in range(1, 4):
        option_name = row.get(f"Option{i} Name", "")
        option_value = row.get(f"Option{i} Value", "")
        if option_name and all(option_value):
            options.append(
                {"name": option_name, "values": [{"name": v} for v in option_value]}
            )

    # Build product input for GraphQL
    product_input = {
        "title": row["Title"],
        "descriptionHtml": row["Body (HTML)"],
        "vendor": row["Vendor"],
        "productType": row["Type"],
        "tags": [tag.strip() for tag in row.get("Tags", []) if tag.strip()],
        "productOptions": options,
    }

    product_media = [
        {
            "originalSource": img,
            "mediaContentType": "IMAGE",
        }
        for img in [*row["Image Src"], *row["Variant Image"]]
        if img
    ]

    # GraphQL mutation
    query = CREATE_PRODUCT_QUERY
    result = graphql_request(store_url, access_token, query, {"product": product_input})

    # === create media ===
    media_query = CREATE_PRODUCT_MEDIA_QUERY
    product_id = result["data"]["productCreate"]["product"]["id"]

    if product_media:
        result_media = graphql_request(
            store_url,
            access_token,
            media_query,
            {
                "media": product_media,
                "productId": product_id,
            },
        )

        if errors := result_media.get("errors"):
            # print all messages from errors list
            print(
                "Error creating product media:",
                ". ".join([e.get("message", []) for e in errors]),
            )

    return result["data"]["productCreate"]


def upload_products_from_csv(
    store_url: str, access_token: str, csv_file_path: str
) -> list[str]:
    products = []

    df = pd.read_csv(csv_file_path).fillna(value="")

    try:
        grouped_df = (
            df.groupby("Handle")
            .aggregate(
                {
                    "Title": "first",
                    "Body (HTML)": "first",
                    "Vendor": "first",
                    "Type": "first",
                    "Tags": list,
                    "Option1 Name": "first",
                    "Option1 Value": lambda x: x.unique().tolist(),
                    "Option2 Name": "first",
                    "Option2 Value": lambda x: x.unique().tolist(),
                    "Option3 Name": "first",
                    "Option3 Value": lambda x: x.unique().tolist(),
                    "Variant SKU": lambda x: x.unique().tolist(),
                    "Variant Price": list,
                    "Variant Requires Shipping": list,
                    "Variant Taxable": list,
                    "Variant Inventory Tracker": list,
                    "Variant Inventory Policy": list,
                    "Variant Fulfillment Service": list,
                    "Variant Grams": list,
                    "Variant Weight Unit": list,
                    "Image Src": list,
                    "Variant Image": list,
                }
            )
            .reset_index()
        )

    except KeyError:
        grouped_df = (
            df.groupby("Title")
            .aggregate(
                {
                    "Body (HTML)": "first",
                    "Vendor": "first",
                    "Type": "first",
                    "Tags": list,
                    "Option1 Name": "first",
                    "Option1 Value": lambda x: x.unique().tolist(),
                    "Option2 Name": "first",
                    "Option2 Value": lambda x: x.unique().tolist(),
                    "Option3 Name": "first",
                    "Option3 Value": lambda x: x.unique().tolist(),
                    # get unique skus
                    "Variant SKU": lambda x: x.unique().tolist(),
                    "Variant Price": list,
                    "Variant Requires Shipping": list,
                    "Variant Taxable": list,
                    "Variant Inventory Tracker": list,
                    "Variant Inventory Policy": list,
                    "Variant Fulfillment Service": list,
                    "Variant Grams": list,
                    "Variant Weight Unit": list,
                    "Image Src": list,
                    "Variant Image": list,
                }
            )
            .reset_index()
        )

    for _, row in grouped_df.iterrows():
        print(f"Uploading product: {row['Title']}")
        product = upload_product(store_url, access_token, row)
        products.append(product["product"]["id"])

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
        print(f"Product {product_id} published with ID: {published_product_id}")
        published_product_ids.append(published_product_id)
    return published_product_ids

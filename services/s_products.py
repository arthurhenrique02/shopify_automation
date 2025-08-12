from itertools import product

import httpx
import pandas as pd
from pandas.core.series import Series

from services.graphql.admin_api import graphql_request
from services.graphql.queries import (  # NOQA: F401
    BULK_CREATE_VARIANTS_QUERY,
    CREATE_PRODUCT_QUERY,
    PUBLISH_PRODUCT_QUERY,
)


def upload_product(
    client: httpx.Client, store_url: str, access_token: str, row: Series
) -> dict:
    options = []
    pos = 1
    for i in range(1, 4):
        option_name = row.get(f"Option{i} Name", "")
        option_value = row.get(f"Option{i} Value", "")
        if option_name and all(option_value):
            options.append(
                {
                    "name": option_name,
                    "position": pos,
                    "values": [{"name": v} for v in option_value],
                }
            )
            pos += 1

    # Build product input for GraphQL
    product_input = {
        "title": row["Title"],
        "descriptionHtml": row["Body (HTML)"],
        "vendor": row["Vendor"],
        "productType": row["Type"],
        "tags": [tag.strip() for tag in row.get("Tags", []) if tag.strip()],
        "productOptions": options,
    }

    medias = [
        {
            "originalSource": img,
            "mediaContentType": "IMAGE",
        }
        for img in [*row["Image Src"], *row["Variant Image"]]
        if img
    ]

    # GraphQL mutation
    result = graphql_request(
        client,
        store_url,
        access_token,
        CREATE_PRODUCT_QUERY,
        {"product": product_input, "media": medias},
    )

    if len(options) > 1:
        p_id = result["data"]["productCreate"]["product"]["id"]
        graphql_request(
            client,
            store_url,
            access_token,
            BULK_CREATE_VARIANTS_QUERY,
            {
                "productId": p_id,
                "variants": [
                    {"optionValues": [*combination]}
                    for i, combination in enumerate(
                        product(
                            *[
                                [
                                    {"optionName": opt["name"], **val}
                                    for val in opt["values"]
                                ]
                                for opt in options
                            ],
                        )
                    )
                    if i > 0
                ],
            },
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

    counter = 0
    with httpx.Client() as client:
        for _, row in grouped_df.iterrows():
            counter += 1
            print(f"Uploading product {counter}: {row['Title']}")
            product = upload_product(client, store_url, access_token, row)
            products.append(product["product"]["id"])

    return products


def publish_product(
    client: httpx.Client,
    store_url: str,
    access_token: str,
    product_id: str,
    publication_id: str,
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
        client,
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

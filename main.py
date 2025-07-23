import csv
import json
import pathlib
import time

from services.automation.core import automation_main
from services.graphql.admin_api import graphql_request
from services.graphql.queries import (
    CREATE_PRODUCT_MEDIA_QUERY,
    CREATE_PRODUCT_QUERY,
    CREATE_VARIANT_QUERY,
)
from services.s_collections import add_product_to_collection, create_collection
from services.s_theme import upload_shopify_theme


def create_product_from_csv_row(row):
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


def main():
    upload_shopify_theme(
        (pathlib.Path(__file__).parent / "assets" / "Tema_Vitrine_Latam")
    )

    raise

    with open("collections.json", encoding="utf-8") as f:
        collections = json.load(f)
    collection_ids = {}

    for name in collections:
        collection_id = create_collection(name)
        collection_ids[name] = collection_id
        # wait rate limit
        time.sleep(0.5)

    with open("100_spanish_products.csv", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            product_id = create_product_from_csv_row(row)
            time.sleep(0.5)

            best_collection_id = collection_ids.get("Best Products")
            if best_collection_id:
                add_product_to_collection(product_id, best_collection_id)
                time.sleep(0.5)


def run_automation():
    automation_main()


if __name__ == "__main__":
    run_automation()


# path to create api token
#   div: AppFrameNav
#   btn: class="_Button_1g3wt_32" span:text="Apps"
#   div: class="_SearchResultSection_izb45_1 _FooterSection_izb45_26"
#   ul: search-results
#   li: app-search-result-apps-and-channels-settings
#   a (click)

# quickest:
#   div: AppFrameTopBar
#   btn: class="_TopBarButton_ale7v_2 _SearchActivator_8d1vr_4"
#   div: search-container -> input: role="combobox"
#   type text
#   div: class="_SearchResultSection_izb45_1"
#   li: gid://shopify/SettingsLink/apps|list
#   a: click

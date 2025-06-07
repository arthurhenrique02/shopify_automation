import csv
import json
import time

from graphql import graphql_request


def create_collection(title):
    query = """
    mutation createCollectionMetafields($input: CollectionInput!) {
      collectionCreate(input: $input) {
        collection {
          id
          title
        }
        userErrors {
          field
          message
        }
      }
    }
    """
    variables = {"input": {"title": title}}
    data = graphql_request(query, variables)
    print(data)
    return data["data"]["collectionCreate"]["collection"]["id"]


def add_product_to_collection(product_id, collection_id):
    query = """
    mutation {
      collectionAddProducts(collectionId: "%s", productIds: ["%s"]) {
        collection {
          title
        }
        userErrors {
          field
          message
        }
      }
    }
    """ % (collection_id, product_id)
    graphql_request(query)


def create_product_from_csv_row(row):
    title = row["Title"]
    body_html = row["Body (HTML)"]
    vendor = row["Vendor"]
    product_type = row["Type"]
    tags = row["Tags"].split(",") if row["Tags"] else []
    options = []

    # Handle options (like Cor, Tamanho)
    if row["Option1 Name"]:
        options.append({"name": row["Option1 Name"], "values": [row["Option1 Value"]]})
    if row["Option2 Name"]:
        options.append({"name": row["Option2 Name"], "values": [row["Option2 Value"]]})
    if row["Option3 Name"]:
        options.append({"name": row["Option3 Name"], "values": [row["Option3 Value"]]})

    # Prepare variant
    variant = {
        "sku": row["Variant SKU"],
        "price": row["Variant Price"],
        "requiresShipping": row["Variant Requires Shipping"].lower() == "true",
        "taxable": row["Variant Taxable"].lower() == "true",
        "inventoryManagement": row["Variant Inventory Tracker"] or None,
        "inventoryPolicy": row["Variant Inventory Policy"] or "continue",
        "fulfillmentService": row["Variant Fulfillment Service"] or "manual",
        "weight": float(row["Variant Grams"] or 0) / 1000.0,  # convert grams to kg
        "weightUnit": row["Variant Weight Unit"] or "kg",
    }

    # Build product input for GraphQL
    product_input = {
        "title": title,
        "bodyHtml": body_html,
        "vendor": vendor,
        "productType": product_type,
        "tags": tags,
        "options": options,
        "variants": [variant],
    }

    # Add image
    if row["Image Src"]:
        product_input["images"] = [{"src": row["Image Src"]}]
        # Variant image
        if row["Variant Image"]:
            variant["image"] = {"src": row["Variant Image"]}

    # GraphQL mutation
    query = """
    mutation productCreate($input: ProductInput!) {
      productCreate(input: $input) {
        product {
          id
          title
        }
        userErrors {
          field
          message
        }
      }
    }
    """
    result = graphql_request(query, {"input": product_input})
    return result["data"]["productCreate"]


def main():
    with open("collections.json") as f:
        collections = json.load(f)

    collection_ids = {}
    for name in collections:
        print(f"Creating collection: {name}")
        collection_id = create_collection(name)
        collection_ids[name] = collection_id
        time.sleep(0.5)  # Respect rate limits

    with open("100_spanish_products.csv", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            print(f"Creating product: {row['title']}")
            product_id = create_product_from_csv_row(row)
            time.sleep(0.5)

            best_collection_id = collection_ids.get("Best Products")
            if best_collection_id:
                print(f"Adding {row['title']} to Best Products")
                add_product_to_collection(product_id, best_collection_id)
                time.sleep(0.5)


if __name__ == "__main__":
    input("digite o token")
    main()


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

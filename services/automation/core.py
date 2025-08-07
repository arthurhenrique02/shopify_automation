import json
import pathlib
import typing

from dotenv import load_dotenv

from services.automation.auth import login
from services.automation.navigation import (
    go_to_shopify_login_page,
)
from services.automation.utils import (
    create_theme_access_password,
    download_theme_access,
    get_custom_app_api_key,
    get_theme_access_password_from_email,
    initialize_driver,
)
from services.graphql.admin_api import graphql_request
from services.s_collections import publish_collections, upload_collections
from services.s_products import publish_products, upload_products_from_csv
from services.s_theme import get_theme_id, upload_shopify_theme

load_dotenv()


def automation_main(
    country: typing.Literal["es", "it"], username: str = None, password: str = None
):
    if country not in ["es", "it"]:
        raise ValueError("Country must be either 'es' (Spain) or 'it' (Italy).")

    if not username or not password:
        raise ValueError("Username and password must be provided.")

    # get items from corresponding country
    assets_folder_path = pathlib.Path(__file__).parent.parent.parent / "assets"
    match country:
        case "es":
            csv_file_path = assets_folder_path / "100_spanish_products.csv"
            theme_folder = assets_folder_path / "Tema_Espanha"
            with open(assets_folder_path / "spanish_collections.json", "r") as file:
                collections = json.load(file)
        case "it":
            csv_file_path = assets_folder_path / "italian_products.csv"
            theme_folder = assets_folder_path / "Tema_Italia"
            with open(assets_folder_path / "italian_collections.json", "r") as file:
                collections = json.load(file)

    driver = initialize_driver()

    go_to_shopify_login_page(driver)

    login(driver, username=username, password=password)

    success, old_handler = download_theme_access(driver)

    store_url = (
        f"{driver.current_url.replace('https://', '').split('/')[2]}.myshopify.com"
    )

    if not success:
        print(
            "Failed to download theme access. Please check your credentials and try again."
        )
        driver.quit()
        return

    success = create_theme_access_password(driver)

    if not success:
        print(
            "Failed to retrieve theme access password. Please check your credentials."
        )
        driver.quit()
        return

    theme_access_password = get_theme_access_password_from_email(driver, store_url)

    if not theme_access_password:
        print(
            "Failed to retrieve theme access password from email. Please check your email settings."
        )
        driver.quit()
        return

    driver.close()
    driver.switch_to.window(old_handler)

    custom_app_api_key = get_custom_app_api_key(driver=driver)

    if not custom_app_api_key:
        print(
            "Failed to retrieve the custom app API key. Please check your credentials."
        )
        driver.quit()
        return

    theme_id = get_theme_id(store_url, theme_access_password)

    if not theme_id:
        print("Theme ID could not be retrieved. Exiting upload process.")
        driver.quit()
        return

    # === PUBLICATIONS ===
    publications = graphql_request(
        store_url=store_url,
        access_token=custom_app_api_key,
        query="{publications(first: 2) { edges { node { id name } } } }",
        variables=None,
    )

    for publication in publications["data"]["publications"]["edges"]:
        if publication["node"]["name"] != "Online Store":
            continue

        online_store_publication_id = publication["node"]["id"]
        break

    if not online_store_publication_id:
        print("Online Store publication not found. Exiting upload process.")
        driver.quit()
        return

    # === COLLECTIONS ===
    collections_id = upload_collections(
        store_url=store_url,
        access_token=custom_app_api_key,
        collections=collections,
    )

    publish_collections(
        store_url=store_url,
        access_token=custom_app_api_key,
        collection_ids=collections_id,
        publication_id=online_store_publication_id,
    )

    # === PRODUCTS ===
    products_id = upload_products_from_csv(
        store_url,
        custom_app_api_key,
        csv_file_path=csv_file_path,
    )

    publish_products(
        store_url=store_url,
        access_token=custom_app_api_key,
        product_ids=products_id,
        publication_id=online_store_publication_id,
    )

    upload_shopify_theme(
        theme_id=theme_id,
        folder_path=theme_folder,
        store_name=store_url,
        password=custom_app_api_key,
    )

    # keep browser alive
    input("Press Enter to close the browser...")

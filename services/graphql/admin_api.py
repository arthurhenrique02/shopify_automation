import os

import httpx
from dotenv import load_dotenv

load_dotenv()

API_VERSION = os.getenv("API_VERSION")

HEADERS = {
    "X-Shopify-Access-Token": "",
    "Content-Type": "application/json; charset=utf-8",
}

BASE_URL = "https://{SHOP_NAME}/admin/api/{API_VERSION}"


def graphql_request(
    store_url: str, access_token: str, query: str, variables: dict | None = None
):
    if not store_url or not access_token:
        raise ValueError("Shop name and access token must be provided.")

    HEADERS["X-Shopify-Access-Token"] = access_token

    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    response = httpx.post(
        f"{BASE_URL}/graphql.json".format(SHOP_NAME=store_url, API_VERSION=API_VERSION),
        headers=HEADERS,
        json=payload,
    )
    response.raise_for_status()
    return response.json()


def update_theme_data(
    shop_name: str, access_token: str, theme_id: str, settings_data: dict
):
    if not shop_name or not access_token or not theme_id:
        raise ValueError("Shop name, access token, and theme ID must be provided.")

    HEADERS["X-Shopify-Access-Token"] = access_token

    response = httpx.put(
        f"{BASE_URL}/themes/{theme_id}/assets.json".format(
            SHOP_NAME=shop_name, API_VERSION=API_VERSION
        ),
        headers=HEADERS,
        json={
            "asset": {
                "key": "config/settings_data.json",
                "value": settings_data,
            }
        },
    )
    response.raise_for_status()
    return response.json()


def get_settings_data_content(shop_name: str, access_token: str, theme_id: str) -> dict:
    if not shop_name or not access_token or not theme_id:
        raise ValueError("Shop name, access token, and theme ID must be provided.")

    HEADERS["X-Shopify-Access-Token"] = access_token

    response = httpx.get(
        f"{BASE_URL}/themes/{theme_id}/assets.json".format(
            SHOP_NAME=shop_name, API_VERSION=API_VERSION
        ),
        headers=HEADERS,
        params={"asset[key]": "config/settings_data.json"},
    )
    response.raise_for_status()
    return response.json()

import os

import httpx
from dotenv import load_dotenv

load_dotenv()

SHOP_NAME = os.getenv("SHOP_NAME")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
API_VERSION = os.getenv("API_VERSION")

HEADERS = {
    "X-Shopify-Access-Token": ACCESS_TOKEN,
    "Content-Type": "application/json; charset=utf-8",
}

BASE_URL = f"https://{SHOP_NAME}/admin/api/{API_VERSION}/graphql.json"


def graphql_request(query, variables=None):
    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    response = httpx.post(BASE_URL, headers=HEADERS, json=payload)
    response.raise_for_status()
    return response.json()

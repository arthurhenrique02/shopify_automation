import os

import httpx
from dotenv import load_dotenv

load_dotenv()


def get_board_lists(board_id: str) -> list:
    """
    Fetches the lists of a specific Trello board using the Trello API.
    """
    url = f"https://api.trello.com/1/boards/{board_id}/lists"
    params = {
        "key": os.getenv("TRELLO_API_KEY"),
        "token": os.getenv("TRELLO_TOKEN"),
    }

    response = httpx.get(url, params=params)
    response.raise_for_status()
    return response.json()


def get_cards_from_list(list_id: str) -> list:
    """
    Fetches the cards from a specific Trello list using the Trello API.
    """
    url = f"https://api.trello.com/1/lists/{list_id}/cards"
    params = {
        "key": os.getenv("TRELLO_API_KEY"),
        "token": os.getenv("TRELLO_TOKEN"),
    }

    response = httpx.get(url, params=params)
    response.raise_for_status()
    return response.json()


def get_card_description(card: dict) -> str:
    """
    Fetches the description of a specific Trello card using the Trello API.
    """
    return card.get("desc", "")


if __name__ == "__main__":
    lists = get_board_lists(os.getenv("TRELLO_BOARD_ID"))
    new_items_list = next(
        filter(lambda x: "NOVA SOLICITAÇÃO" in x["name"], lists), None
    )

    if not new_items_list:
        raise ValueError("List not found")

    cards = get_cards_from_list(new_items_list["id"])

    # TODO USE CARDS DATA INTO AUTOMATION CORE TO PROCESS

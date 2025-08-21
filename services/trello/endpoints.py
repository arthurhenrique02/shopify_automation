import os

import httpx
import instructor
from dotenv import load_dotenv

from models.user import TrelloUserData

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


def get_user_info_from_description(description: str) -> TrelloUserData:
    """
    Extracts user information from the card description using the Instructor AI model.
    """
    client = instructor.from_provider("ollama/qwen3:0.6b", mode=instructor.Mode.JSON)
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": (
                    f"You're a text scrapper and received some text to extract infomration. "
                    "Follow the insctructions below:\n"
                    "1. Extract the name, email, password, country, phone, store name, and colors from the text.\n"
                    "2. The country should be one option ('non' if country not in the list).\n"
                    "3. Transform color data into hexadecimal string. (Example: white: #ffffff, black: #000000, etc)\n"
                    f"The text is: {description}"
                ),
            },
        ],
        response_model=TrelloUserData,
        max_retries=2,
    )
    return response

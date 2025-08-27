import os

from services.automation.core import automation_main
from services.trello.endpoints import (
    get_board_lists,
    get_card_description,
    get_cards_from_list,
    get_user_info_from_description,
)


def main():
    lists = get_board_lists(os.getenv("TRELLO_BOARD_ID"))
    new_items_list = next(
        filter(lambda x: "NOVA SOLICITAÇÃO" in x["name"], lists), None
    )

    if not new_items_list:
        raise ValueError("List not found")

    cards = get_cards_from_list(new_items_list["id"])

    for card in cards:
        description = get_card_description(card)
        if not description:
            continue

        user_data = get_user_info_from_description(description)

        automation_main(
            country=user_data.country,
            username=user_data.email,
            password=user_data.password,
            card_id=card["id"],
            trello_lists=lists,
        )


if __name__ == "__main__":
    main()

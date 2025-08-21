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
        )


if __name__ == "__main__":
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

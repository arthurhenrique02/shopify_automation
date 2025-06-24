import os

from dotenv import load_dotenv

from services.automation.auth import login
from services.automation.navigation import (
    go_to_create_app_page,
    go_to_shopify_login_page,
)
from services.automation.utils import initialize_driver

load_dotenv()


def automation_main():
    driver = initialize_driver()

    go_to_shopify_login_page(driver)

    login(driver, username=os.getenv("username"), password=os.getenv("password"))

    go_to_create_app_page(driver)

    # keep browser alive
    input("Press Enter to close the browser...")

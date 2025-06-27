import os

from dotenv import load_dotenv

from services.automation.auth import login
from services.automation.navigation import (
    go_to_shopify_login_page,
)
from services.automation.utils import (
    create_theme_access_password,
    download_theme_access,
    initialize_driver,
)

load_dotenv()


def automation_main():
    driver = initialize_driver()

    go_to_shopify_login_page(driver)

    login(driver, username=os.getenv("username"), password=os.getenv("password"))

    success, old_handler = download_theme_access(driver)

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

    # keep browser alive
    input("Press Enter to close the browser...")

import os

from dotenv import load_dotenv

from services.automation.auth import login
from services.automation.navigation import (
    go_to_shopify_login_page,
    open_create_app_page,
)
from services.automation.utils import (
    create_theme_access_password,
    download_theme_access,
    enable_custom_dev_mode,
    get_theme_access_password_from_email,
    initialize_driver,
)

load_dotenv()


def automation_main():
    driver = initialize_driver()

    go_to_shopify_login_page(driver)

    login(driver, username=os.getenv("username"), password=os.getenv("password"))

    success, old_handler = download_theme_access(driver)

    store_name = driver.current_url.replace("https://", "").split("/")[2]

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

    theme_access_password = get_theme_access_password_from_email(driver, store_name)

    # TODO: CREATE CUSTOM APP
    driver.close()
    driver.switch_to.window(old_handler)

    old_handler = open_create_app_page(driver)

    driver.switch_to.window(driver.window_handles[-1])
    enable_custom_dev_mode(driver)

    if not success:
        print("Failed to open the create app page. Please check your credentials.")
        driver.quit()
        return

    # keep browser alive
    input("Press Enter to close the browser...")

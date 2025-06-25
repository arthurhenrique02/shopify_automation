from selenium.webdriver.remote.webdriver import WebDriver


def go_to_shopify_login_page(driver):
    driver.get("https://admin.shopify.com/login?errorHint=no_cookie_auth_token")


def open_create_app_page(driver) -> str:
    """
    Navigate to the page for creating a new app in Shopify admin.
    :param driver: Selenium WebDriver instance
    :return: Old window handle to return to later
    """
    handler = driver.current_window_handle

    driver.execute_script(
        "window.open('https://admin.shopify.com/settings/apps/development', '_blank');"
    )

    return handler


def open_theme_access_download_page(driver: WebDriver) -> str:
    """
    Navigate to the theme access and download page in Shopify admin.
    :param driver: Selenium WebDriver instance\
    return: Old window handle to return to later
    """
    handler = driver.current_window_handle

    driver.execute_script(
        "window.open('https://apps.shopify.com/theme-access', '_blank');"
    )

    driver.switch_to.window(driver.window_handles[-1])

    return handler

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .utils import find_submit_button


def login(driver: WebDriver, username: str, password: str):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "account_email"))
    ).send_keys(username)

    find_submit_button(driver=driver).click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "account_password"))
    ).send_keys(password)

    find_submit_button(driver=driver).click()

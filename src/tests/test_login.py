# src/tests/test_login.py
import allure
import pytest

from pages.login_page import LoginPage
from utils.logger import get_logger
logger = get_logger(__name__)

class TestLogin:

    @allure.title("Login with valid credentials")
    def test_login_valid_user(self, driver, config):
        logger.info("Testing login with valid credentials")
        login_page = LoginPage(driver)
        login_page.login(config["username"], config["password"])
        assert "Dashboardpage" in driver.title


    # def test_login_invalid_user(self, driver):
    #     login_page = LoginPage(driver)
    #     login_page.login("wronguser", "wrongpass")
    #     # assert login_page.get_error_message() == "Invalid credentials"

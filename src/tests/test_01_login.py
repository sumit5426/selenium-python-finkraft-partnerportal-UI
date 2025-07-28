# src/tests/test_01_login.py
from pyexpat.errors import messages

import allure
import pytest

from pages.login_page import LoginPage
from utils.logger import get_logger
logger = get_logger(__name__)

class TestLogin:

    @allure.epic("User Management")
    @allure.feature("Login")
    @allure.story("As an user I can log in")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("smoke","all_client")
    @pytest.mark.smoke
    @allure.title("Login with valid credentials")
    def test_login_valid_user(self, driver, config):
        logger.info("Testing login with valid credentials")
        login_page = LoginPage(driver)
        login_page.login(config["username"], config["password"])
        if "dashboard" not in login_page.page_title():
            logger.error("Login failed – 'dashboard' not found in page title")
            pytest.exit("Login failed! Stopping test execution.")


    @pytest.mark.regression
    @allure.title("Login with empty username")
    def test_login_empty_username(self, driver):
        logger.info("Testing login with empty fields")
        login_page = LoginPage(driver)
        error_message=login_page.login_empty_username("")
        assert error_message == "Please enter your email!", \
            f"Expected error 'Please enter your email!' but got '{error_message}'"


    @allure.title("Login with invalid credentials")
    def test_login_invalid_user_details(self, driver):
        login_page = LoginPage(driver)
        boolean_result=login_page.login_invalid_details("abc@gmail.com", "wrongpass")
        assert boolean_result, \
       f"Expected Sign-In URL, but got: {driver.current_url}"

    @allure.title("Login and logout")
    def test_login_logout(self, driver, config):
        logger.info("Testing login and logout")
        login_page = LoginPage(driver)
        boolean_result=login_page.login_logout(config["username"], config["password"])
        assert boolean_result, \
            f"Expected Sign-In URL, but got: {driver.current_url}"
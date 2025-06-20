import allure
from selenium.webdriver.common.by import By

from pages.dashboard_page import DashBoardPage
from utils.browser_utility import BrowserUtility
from utils.logger import get_logger
logger = get_logger(__name__)


class LoginPage(BrowserUtility):
    def __init__(self, driver):
        super().__init__(driver)

    EMAIL_TEXTBOX = (By.XPATH, "//input[@placeholder='Email']")
    PASSWORD_TEXTBOX = (By.XPATH, "//input[@placeholder='Password']")
    SUBMIT_BUTTON = (By.XPATH, '//button[@type="submit"]')
    SIGNIN_BUTTON = (By.CSS_SELECTOR, 'button[type="submit"]')

    @allure.feature("Login Feature")
    @allure.step("Enter email and password")
    @allure.severity(allure.severity_level.CRITICAL)
    def login(self, username, password):
        logger.info(f"Logging in with user: {username}")
        self.enter_text(self.EMAIL_TEXTBOX, username)
        self.click(self.SUBMIT_BUTTON)
        self.enter_text(self.PASSWORD_TEXTBOX, password)
        self.click(self.SUBMIT_BUTTON)
        print("Logging in with email:", username)
        dashboard_page=DashBoardPage(self.driver)
        return dashboard_page



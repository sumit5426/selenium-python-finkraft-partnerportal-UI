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
    ERROR_MESSAGE = (By.XPATH, '//div[@class="ant-form-item-explain-error"]')
    PROFILE_ICON = (By.XPATH,'(//span[@class="ant-avatar-string"])[1]')
    LOGOUT_BUTTON = (By.XPATH, "// div[normalize-space()='Logout']")


    @allure.feature("Login Feature")
    @allure.step("Enter email and password and click Sign In.")
    @allure.severity(allure.severity_level.CRITICAL)
    def login(self, username, password):
        logger.info(f"Logging in with user: {username}")
        self.enter_text(self.EMAIL_TEXTBOX, username)
        self.click(self.SUBMIT_BUTTON)
        self.enter_text(self.PASSWORD_TEXTBOX, password)
        self.click(self.SUBMIT_BUTTON)
        logger.info(f"Logged in with user: {username}")
        dashboard_page=DashBoardPage(self.driver)
        return dashboard_page

    def login_logout(self, username, password):
        self.enter_text(self.EMAIL_TEXTBOX, username)
        self.click(self.SUBMIT_BUTTON)
        self.enter_text(self.PASSWORD_TEXTBOX, password)
        self.click(self.SUBMIT_BUTTON)
        self.click(self.PROFILE_ICON)
        self.click(self.LOGOUT_BUTTON)
        return self.is_signin_page_url()


    def login_empty_username(self, username):
        logger.info(f"Logging in with user: {username}")
        self.enter_text(self.EMAIL_TEXTBOX, username)
        self.click(self.SUBMIT_BUTTON)
        return self.visible_text(self.ERROR_MESSAGE)

    def login_invalid_details(self, username,password):
        logger.info(f"Logging in with user: {username}")
        self.enter_text(self.EMAIL_TEXTBOX, username)
        self.click(self.SUBMIT_BUTTON)
        self.enter_text(self.PASSWORD_TEXTBOX, password)
        self.click(self.SUBMIT_BUTTON)
        return self.is_signin_page_url()




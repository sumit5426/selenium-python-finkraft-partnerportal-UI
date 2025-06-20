import time

from selenium.common import ElementClickInterceptedException
from selenium.webdriver.common.by import By

from utils.browser_utility import BrowserUtility


class DashBoardPage(BrowserUtility):
    def __init__(self,driver):
        super().__init__(driver)

    SWITCH_WORKSPACE_LOGO = (By.XPATH,"//div[contains(@class,'ant-dropdown-trigger')]")


    def switch_workspace(self,workspace_name):
        print("Switching workspace from page class")
        self.click(self.SWITCH_WORKSPACE_LOGO)
        WORKSPACE=(By.XPATH, f"//p[normalize-space()='{workspace_name}']")
        self.click_scroll(WORKSPACE)

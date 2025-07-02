import time

from selenium.common import ElementClickInterceptedException
from selenium.webdriver.common.by import By

from utils.browser_utility import BrowserUtility
from utils.logger import get_logger
logger = get_logger(__name__)


class DashBoardPage(BrowserUtility):
    def __init__(self,driver):
        super().__init__(driver)

    SWITCH_WORKSPACE_LOGO = (By.XPATH,"//div[contains(@class,'ant-dropdown-trigger')]")
    WORKSPACE_NAME=(By.XPATH,"//p[contains(@class,'sc-Qotzb')][normalize-space()='Reserve bank of india yatra']")
    IFRAME_LOCATOR = (By.ID, "dashboardFrame")
    MODULE_LIST_LOCATOR = (By.CSS_SELECTOR, ".MenuItem")
    TOP_SUB_MODULE_LOCATOR = (By.XPATH, '//div[@class="ant-tabs-tab-btn"]')  # Adjust as per your HTML

    WIDGET_LOCATORS = {
        "logo": {
            "locator": (By.XPATH, "//img[@alt='appIcon']"),
            "in_iframe": False
        },
        "piechart": {
            "locator": (By.CSS_SELECTOR, ".piegroup"),
            "in_iframe": True
        },
        "tables": {
            "locator": (By.CSS_SELECTOR, ".scrollFreeze"),
            "in_iframe": True
        },
        "tables_filter": {
            "locator": (By.XPATH,'//div[@class="ZR-DashboardUFContainer"]//div[@elname="filterHead"]'),
            "in_iframe": True
        },
        "dashboard_filter": {
            "locator": (By.XPATH, '//div[@class="ant-tabs-tab-btn"]'),
            "in_iframe": False
        },
        "menu_item": {
            "locator": (By.CSS_SELECTOR, '.MenuItem'),
            "in_iframe": False
        },

        # Add more widgets as needed
    }

    def switch_workspace(self,workspace_name):
        print("Switching workspace from page class")
        self.click(self.SWITCH_WORKSPACE_LOGO)
        WORKSPACE=(By.XPATH, f"//p[normalize-space()='{workspace_name}']")
        self.click_scroll(WORKSPACE)
        return self.visible_text(self.WORKSPACE_NAME)

    def switch_to_dashboard_iframe(self):
        iframe = self.driver.find_element(*self.IFRAME_LOCATOR)
        self.driver.switch_to.frame(iframe)

    def is_widget_visible(self, widget_name, timeout=10):
        widget_info = self.WIDGET_LOCATORS.get(widget_name)
        if not widget_info:
            logger.warning(f"No locator defined for widget: {widget_name}")
            return False
        locator = widget_info["locator"]
        in_iframe = widget_info.get("in_iframe", False)
        try:
            if in_iframe:
                self.switch_to_dashboard_iframe()
            element = self.visible_element(locator, timeout=timeout)
            result = element.is_displayed() if element else False
            logger.info(f"Widget '{widget_name}' is visible: {result}")
            return result
        except Exception as e:
            logger.error(f"Exception for widget '{widget_name}': {e}")
            return False
        finally:
            if in_iframe:
                self.driver.switch_to.default_content()

    def get_visible_modules(self):
        """Return a list of visible module names from sidebar."""
        elements = self.driver.find_elements(*self.MODULE_LIST_LOCATOR)
        return [el.text.strip() for el in elements if el.is_displayed() and el.text.strip()]

    def are_modules_present(self, expected_modules: list[str]) -> list[str]:
        """Returns the list of modules from expected_modules that are missing from UI."""
        visible_modules = self.get_visible_modules()
        missing = [mod for mod in expected_modules if mod not in visible_modules]
        return missing

    def get_top_horizontal_modules(self):
        elements = self.driver.find_elements(*self.TOP_SUB_MODULE_LOCATOR)
        return [ el.text.strip().lower() for el in elements if el.is_displayed() and el.text.strip() ]

    def are_top_modules_present(self, expected_keywords: list[str]) -> list[str]:
        actual_modules = self.get_top_horizontal_modules()  # e.g., ['dashboard-hotel', 'airline']
        missing = []
        for keyword in expected_keywords:
            if not any(keyword.lower() in mod for mod in actual_modules): missing.append(keyword)
        return missing

    def click_top_module(self, module_name: str):
        modules = self.driver.find_elements(*self.TOP_SUB_MODULE_LOCATOR)
        for module in modules:
            if module.is_displayed() and module_name.lower() in module.text.lower():
                module.click()
                return True
        raise Exception(f"Module '{module_name}' not found or not clickable.")

    MODULE_CONTENT_LOCATOR = (By.CSS_SELECTOR, ".module-content")  # adjust as per your DOM

    def is_module_data_loaded(self):
        content = self.visible_element(self.MODULE_CONTENT_LOCATOR)
        if content:
            return content.is_displayed()
        return False

    SET_VIEW_TITLE_LOCATOR = (By.CSS_SELECTOR, "#setViewTitle")

    def get_module_title_text(self):
        element = self.visible_element(self.SET_VIEW_TITLE_LOCATOR)
        return element.text if element else None

    # def switch_to_dashboard_iframe(self):
    #     try:
    #         # Adjust locator if needed
    #         iframe = self.visible_element((By.CSS_SELECTOR, "iframe"))
    #         self.driver.switch_to.frame(iframe)
    #         print("[switch_to_dashboard_iframe] Switched to dashboard iframe.")
    #     except Exception as e:
    #         raise Exception(f"Failed to switch to iframe: {e}")

    def switch_to_default(self):
        self.driver.switch_to.default_content()
        print("[switch_to_default] Switched back to main content.")








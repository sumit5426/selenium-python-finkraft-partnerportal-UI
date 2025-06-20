from selenium.common import ElementClickInterceptedException, ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BrowserUtility:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def click(self, locator):
        self.wait.until(EC.element_to_be_clickable(locator)).click()
        return self

    def enter_text(self, locator, text):
        self.wait.until(EC.visibility_of_element_located(locator)).send_keys(text)
        return self

    def click_and_enter(self, locator, text):
        self.click(locator)
        self.enter_text(locator, text)
        return self

    def click_scroll(self, locator):
        """Generic click with fallback scroll-into-view if click fails."""
        try:
            self.click(locator)
        except (ElementClickInterceptedException, ElementNotInteractableException):
            print("Element not clickable directly. Scrolling into view and retrying...")
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", locator)

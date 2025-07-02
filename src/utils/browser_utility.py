from selenium.common import ElementClickInterceptedException, ElementNotInteractableException, NoSuchElementException, \
    TimeoutException, NoAlertPresentException
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

    def visible_element(self, locator, timeout=None):
        """Wait until the element is visible. Return the element if found, else None."""
        try:
            # Use default self.wait or override with custom timeout
            print(locator)
            wait = self.wait if timeout is None else WebDriverWait(self.driver, timeout)
            return wait.until(EC.visibility_of_element_located(locator))
        except TimeoutException:
            print(f"[visible_element] Element with locator {locator} not visible after {timeout or 10} seconds.")
            return None

    def visible_text(self, locator):
        """Check if an error message is visible within the given timeout."""
        try:
            element = self.wait.until(
                EC.visibility_of_element_located(locator)
            )
            return element.text
        except TimeoutException:
            return None

    def get_alert_text_if_present(self):
        """
        Checks if a browser alert is present.
        Returns:
            The alert text if alert is present, else None.
        """
        try:
            self.wait.until(EC.alert_is_present())
            print("Alert present.")
            alert = self.driver.switch_to.alert
            return alert.text
        except TimeoutException:
            return None
        except NoAlertPresentException:
            return None

    def is_signin_page_url(self):
        current_url = self.driver.current_url
        is_correct_url = ".finkraft.ai/auth/signin" in current_url
        return is_correct_url




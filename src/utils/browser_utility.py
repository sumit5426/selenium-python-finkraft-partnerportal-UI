import time

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

    def scroll_into_view(self, element):
        """Scroll the page to bring the element into view."""
        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", element)

    def wait_for_all_elements(self, locator):
        """Wait until all elements matching the locator are present in the DOM."""
        try:
            return self.wait.until(EC.presence_of_all_elements_located(locator))
        except TimeoutException:
            print(f"[wait_for_all_elements] Elements with locator {locator} not found within seconds.")
            return []

    def wait_for_value_change(self, old_value, locator, timeout=10):
        self.wait.until(
            lambda driver: self.visible_text(locator)
        )

    def scroll_to_bottom_of_container(self, selector, pause_time=2, max_attempts=10):

        self.wait.until(
            lambda d: d.execute_script(f"return document.querySelector('{selector}') !== null")
        )

        scroll_script = f"""
            const el = document.querySelector('{selector}');
            if (!el) return [-1, -1, -1, false];
            el.scrollTop = el.scrollHeight;
            const scrollTop = el.scrollTop;
            const clientHeight = el.clientHeight;
            const scrollHeight = el.scrollHeight;
            const isBottom = (scrollTop + clientHeight) >= scrollHeight - 2;
            return [scrollTop, clientHeight, scrollHeight, isBottom];
        """

        for attempt in range(max_attempts):
            scrollTop, clientHeight, scrollHeight, isBottom = self.driver.execute_script(scroll_script)
            print(
                f"[Attempt {attempt + 1}] scrollTop: {scrollTop}, clientHeight: {clientHeight}, scrollHeight: {scrollHeight}, atBottom: {isBottom}")
            if isBottom:
                print(f"✅ Reached bottom of {selector}.")
                return True
            time.sleep(pause_time)

        print(f"⚠️ Could not confirm scroll to bottom of {selector}.")
        return False





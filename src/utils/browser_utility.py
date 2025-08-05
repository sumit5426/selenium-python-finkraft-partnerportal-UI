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

    TABLE_HEADING_LABEL_LOCATOR=(By.XPATH,'//span[@ref="eText" and @class="ag-header-cell-text"]')


    def click(self, locator):
        try:
            element = self.wait.until(EC.element_to_be_clickable(locator))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            try:
                element.click()
            except ElementClickInterceptedException:
                self.driver.execute_script("arguments[0].click();", element)
            return self
        except TimeoutException:
            raise Exception(f"[CLICK ERROR] Element not clickable: {locator}")

    def enter_text(self, locator, text):
        self.wait.until(EC.visibility_of_element_located(locator)).send_keys(text)
        return self

    def enter_text_element(self, element, text):
        self.wait.until(EC.visibility_of(element)).send_keys(text)
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
            print(f"text is visible: {element.text}")
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

    def switch_to_iframe(self, iframeLocator):
        try:
            print("⏳ Waiting for dashboard iframe to be available...")
            self.wait.until(
                EC.frame_to_be_available_and_switch_to_it(iframeLocator)
            )
            print("✅ Switched to dashboard iframe")
        except TimeoutException:
            print("❌ Timeout: Could not switch to dashboard iframe.")
            raise

    def switch_to_default_content(self):
        try:
            self.driver.switch_to.default_content()
            print("✅ [switch_to_default_content] Switched back to main content.")
        except Exception as e:
            print(f"❌ Failed to switch to default content: {e}")
            raise

    def get_visible_modules_texts(self,elements):
        """Return a list of visible module names from sidebar."""
        return [el.text.strip() for el in elements if el.is_displayed() and el.text.strip()]

    def is_element_present(self, locator):
        try:
            self.wait.until(EC.presence_of_element_located(locator))
            return True
        except TimeoutException:
            return False

    def to_open_iframe_cors_in_another_tab(self, iframeLocator):
        time.sleep(7)
        iframe = self.driver.find_element(*iframeLocator)
        iframe_url = iframe.get_attribute("src")
        time.sleep(10)
        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[1])  # Switch to new tab
        time.sleep(2)
        self.driver.get(iframe_url)


    def is_no_data_displayed(self,locator,timeout=1):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False


    def ag_table_header_text(self,locator):
        headings = []
        seen = set()
        # Get the scrollable container (usually a div with overflow-x: auto)
        scroll_container = self.driver.find_element(*locator)  # Adjust selector as needed
        # Scroll to the far left
        self.driver.execute_script("arguments[0].scrollLeft = 0;", scroll_container)
        last_scroll = -1
        while True:
            # Collect visible headings
            elements = self.wait_for_all_elements(self.TABLE_HEADING_LABEL_LOCATOR)
            for el in elements:
                text = el.text.strip()
                if text and text not in seen:
                    headings.append(text)
                    seen.add(text)
            # Scroll right by a chunk
            current_scroll = self.driver.execute_script("return arguments[0].scrollLeft;", scroll_container)
            max_scroll = self.driver.execute_script("return arguments[0].scrollWidth - arguments[0].clientWidth;",
                                                    scroll_container)
            print(f"Scrolling... current: {current_scroll}, max: {max_scroll}")
            if current_scroll == max_scroll or current_scroll == last_scroll:
                print("headheadings:" + str(headings))
                break
            self.driver.execute_script("arguments[0].scrollLeft += 440;", scroll_container)
            last_scroll = current_scroll
        return list(headings)

    def clear_text(self,locator,index):
        clear_elements =self.wait_for_all_elements(locator)
        print(f"length {len(clear_elements)}")
        for el in clear_elements:
            print(index)
            el.clear()





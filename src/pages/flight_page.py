import time
from selenium.common import NoSuchElementException
from selenium.webdriver import Keys

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from utils.browser_utility import BrowserUtility


class FlightPage(BrowserUtility):
    def __init__(self, driver):
        super().__init__(driver)

    BODY_SCROLL_LOCATOR=(By.CSS_SELECTOR,".ag-body-horizontal-scroll-viewport")
    TABLE_HEADING_LABEL_LOCATOR=(By.XPATH,'//span[@ref="eText" and @class="ag-header-cell-text"]')
    TOGGLE_BUTTONS_LOCATOR = (By.XPATH, '//button[@ref="eToggleButton"]')
    CHECKBOXES_LOCATOR = (By.XPATH, '//input[contains(@aria-label,"Press SPACE to toggle visibility")]')
    CHECKBOX_LABELS_LOCATOR = (By.CSS_SELECTOR,".ag-column-select-column-label")
    VIRTUAL_LIST_ITEM_LOCATOR = (By.CSS_SELECTOR, '.ag-virtual-list-item')
    COLUMN_SELECTOR_CONTAINER_LOCATOR = (By.CSS_SELECTOR, '.ag-column-select-virtual-list-viewport')
    COLUMN_SELECTOR_TOGGLE_LOCATOR = (By.CSS_SELECTOR, ".column-selector-toggle")
    FILTER_TOGGLES = (By.CSS_SELECTOR, ".ag-group-title")
    TOGGLE_CONTAINER = (By.XPATH, "//div[contains(@class,'ag-group-container')]")
    FILTER_INPUT = (By.XPATH, "//input[@aria-label='Filter Value']")
    SPIN_LOADER_LOCATOR = (By.XPATH,'//span[contains(@class, "ag-loading-icon")]')
    SUB_FILTER_LOCATOR=(By.XPATH,'//div[@ref="eFilterBody"]//div[@aria-label="Filtering operator"]')


    def get_flight_ag_grid_table_headings(self):
        return self.ag_table_header_text(self.BODY_SCROLL_LOCATOR)

    def has_table_headings(self):
        return len(self.driver.find_elements(*self.TABLE_HEADING_LABEL_LOCATOR)) > 0

    def open_column_selector(self, toggle_index=0):
        toggles = self.wait_for_all_elements(self.TOGGLE_BUTTONS_LOCATOR)
        toggles[toggle_index].click()
        # Wait for container to appear
        WebDriverWait(self.driver, 10).until(
            lambda d: d.find_element(*self.COLUMN_SELECTOR_CONTAINER_LOCATOR).is_displayed()
        )

    def get_checkbox_labels(self):
        """
        Returns the list of all checkbox label texts in the selector.
        Scrolls container to top first to ensure consistent ordering.
        """
        container = self.driver.find_element(*self.COLUMN_SELECTOR_CONTAINER_LOCATOR)
        self.driver.execute_script("arguments[0].scrollTop = 0;", container)

        labels = self.driver.find_elements(*self.CHECKBOX_LABELS_LOCATOR)
        return [lbl.text.strip() for lbl in labels]

    def find_checkbox_by_label_with_scroll(self, label_text, max_scroll_attempts=100, scroll_step=100):
        container = self.driver.find_element(*self.COLUMN_SELECTOR_CONTAINER_LOCATOR)
        self.driver.execute_script("arguments[0].scrollTop = 0;", container)
        last_scroll = -1
        attempts = 0
        epsilon = 2

        while attempts < max_scroll_attempts:
            # Wait for label presence after scroll
            found = False
            labels = self.driver.find_elements(*self.CHECKBOX_LABELS_LOCATOR)
            checkboxes = self.driver.find_elements(*self.CHECKBOXES_LOCATOR)
            for lbl, chk in zip(labels, checkboxes):
                if lbl.text.strip() == label_text:
                    found = True
                    return chk

            if not found:
                current_scroll = self.driver.execute_script("return arguments[0].scrollTop;", container)
                max_scroll = self.driver.execute_script("return arguments[0].scrollHeight - arguments[0].clientHeight;",
                                                        container)

                if max_scroll - current_scroll <= epsilon or current_scroll == last_scroll:
                    break

                self.driver.execute_script("arguments[0].scrollTop += arguments[1];", container, scroll_step)

                # Wait until scrollTop increased (scroll applied)
                WebDriverWait(self.driver, 2).until(
                    lambda d: d.execute_script("return arguments[0].scrollTop;", container) > current_scroll
                )

                # Wait for grid rendering to catch up - replace hard sleep with label wait if possible
                time.sleep(0.3)

                last_scroll = current_scroll
                attempts += 1

        raise Exception(f"Checkbox with label '{label_text}' not found after scrolling.")


    def toggle_column(self, label_text, expected_visible, timeout=5):
        """
        Toggles the checkbox for the given label_text and waits
        until its aria-label reflects expected_visible ('visible' or 'hidden').
        """
        chk = self.find_checkbox_by_label_with_scroll(label_text)
        chk.click()

        expected_state = "visible" if expected_visible else "hidden"
        WebDriverWait(self.driver, timeout).until(
            lambda d: expected_state in self.find_checkbox_by_label_with_scroll(label_text)
            .get_attribute("aria-label"),
            message=f"aria-label did not become {expected_state}"
        )

    def get_table_headings(self):
        """
        Returns the list of current table heading texts.
        """
        headers = self.driver.find_elements(*self.TABLE_HEADING_LABEL_LOCATOR)
        return [hdr.text.strip() for hdr in headers]

    def get_toggle_button_count(self):
        elements = self.driver.find_elements(*self.TOGGLE_BUTTONS_LOCATOR)
        return len(elements)


    def click_toggle_button_and_wait(self, index=0, expected_state="true", timeout=5):
        buttons = self.wait_for_all_elements(self.TOGGLE_BUTTONS_LOCATOR)
        button = buttons[index]
        button.click()
        WebDriverWait(self.driver, timeout).until(
            lambda d: button.get_attribute("aria-expanded") == expected_state,
            message=f"aria-expanded did not become {expected_state} after clicking"
        )
        return button.get_attribute("aria-expanded")

    def find_vertical_scrollable_elements(self, selector=".ag-body-viewport"):
        self.scroll_to_bottom_of_container(selector)
        # viewport = WebDriverWait(self.driver, 10).until(
        #     EC.presence_of_element_located((By.CSS_SELECTOR, ".ag-center-cols-viewport"))
        # )
        # self.driver.execute_script("""
        #     arguments[0].scrollTop = arguments[0].scrollHeight;
        #     arguments[0].dispatchEvent(new Event('scroll'));
        # """, viewport)
        # rows = self.driver.find_elements(By.CSS_SELECTOR, "div[role='row']")
        # last_row = rows[-1]
        # self.driver.execute_script("arguments[0].scrollIntoView({block: 'end'});", last_row)
        # In your FlightPage class:

    def scroll_to_bottom_of_aggrid_table(self, timeout=15, max_attempts=10):
        scrollable = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".ag-body-viewport")))
        last_height = -1
        for i in range(max_attempts):
            self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable)
            # Wait for possible lazy loading
            time.sleep(1)
            current_height = self.driver.execute_script("return arguments[0].scrollTop", scrollable)
            if current_height == last_height:
                break  # We've reached the bottom
            last_height = current_height

    def get_filter_toggles(self):
        return self.wait_for_all_elements(self.FILTER_TOGGLES)

    # def get_table_row_count(self):
    #     return len(self.driver.find_elements(*self.TABLE_ROWS))

    def expand_toggle(self, toggle):
        self.driver.execute_script('arguments[0].scrollIntoView({block:"center"});', toggle)
        # if "ag-group-expanded" not in toggle.get_attribute("class"):
        toggle.click()
        time.sleep(0.3)  # Allow for animation

    def collapse_toggle(self, toggle):
        if "ag-group-expanded" in toggle.get_attribute("class"):
            toggle.click()
            time.sleep(0.2)

    def get_inputs_under_toggle(self, toggle, index):
        # toggles=self.get_filter_toggles()
        # input_box=toggles[index+1].find_element(*self.FILTER_INPUT)
        self.clear_text(self.FILTER_INPUT,index)
        toggle = self.driver.find_element(
            By.XPATH,
            f"(//div[contains(@class,'ag-group-container')])[{index + 1}]"
        )
        input_boxes = toggle.find_elements(*self.FILTER_INPUT)
        # Filter visible inputs only
        visible_inputs = [inp for inp in input_boxes if inp.is_displayed()]

        # Type in the first visible input only
        # visible_inputs[0].clear()
        # visible_inputs[0].send_keys(text)
        self.enter_text_element(visible_inputs[0],'abc')
        time.sleep(2)
        self.clear_text(self.FILTER_INPUT,index)

    def wait_for_loader_to_appear(self, timeout=5):
        try:
            self.wait.until(EC.visibility_of_element_located(self.SPIN_LOADER_LOCATOR))
        except Exception:
            print("no loader found")

    def wait_for_loader_to_disappear(self, timeout=10):
        try:
            self.wait.until(EC.invisibility_of_element_located(self.SPIN_LOADER_LOCATOR))
        except Exception:
            print("Not disappeared")


    # def apply_filter_and_check_change(self, input_elem, test_text="abc"):
    #     rows_before = self.get_table_row_count()
    #     input_elem.clear()
    #     input_elem.send_keys(test_text)
    #     input_elem.send_keys(Keys.TAB)
    #     # Wait for table row count to change (can adjust logic for content change)
    #     self.wait.until(lambda d: self.get_table_row_count() != rows_before)
    #     # Optionally: add further assertions or return value
    #     time.sleep(0.3)
    #     input_elem.clear()
    #     input_elem.send_keys(Keys.TAB)
    #     time.sleep(0.2)

    def open_column_selector_filter(self, toggle_index=0):
        toggles = self.wait_for_all_elements(self.TOGGLE_BUTTONS_LOCATOR)
        toggles[toggle_index].click()

    def select_sub_filter(self):
        dropdown=self.visible_element(self.SUB_FILTER_LOCATOR)
        dropdown.click()
        time.sleep(10)
        options_container = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[id^='ag-select-list-']")))
        option_elements = options_container.find_elements(By.CSS_SELECTOR, ".ag-select-list-option")
        print(option_elements)
        print(len(option_elements))









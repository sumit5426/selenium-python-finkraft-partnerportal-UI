import random
from operator import index

import time
from selenium.common import NoSuchElementException
from selenium.webdriver import Keys, ActionChains

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

    def get_column_headers(self):
        elements = self.wait_for_all_elements(self.TABLE_HEADING_LABEL_LOCATOR)
        return elements[:-2]

    def get_column_header_names(self):
        return self.driver.execute_script("""
                    return Array.from(document.querySelectorAll('.ag-header-cell'))
                        .sort((a, b) => a.getAttribute('aria-colindex') - b.getAttribute('aria-colindex'))
                        .map(el => el.innerText.trim());
                """)

    def drag_and_drop_column(self, source, target):
        self.driver.execute_script("arguments[0].scrollIntoView(true);", source)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", target)
        actions = ActionChains(self.driver)
        actions.click_and_hold(source).move_to_element(target).pause(0.5).release().perform()

    def wait_for_header_order_change(self, old_order, timeout=10):
        def _order_changed(driver):
            # Always re-fetch the header names from the DOM
            try:
                new_order = self.get_column_header_names()
                print("Checking new order:", new_order)
                return new_order != old_order
            except Exception as e:
                print("Exception while checking header order:", e)
                return False

        WebDriverWait(self.driver, timeout).until(
            _order_changed,
            message=f"[TIMEOUT] Header order did not update in {timeout}s."
        )


    def drag_and_drop_two_random_headers(self, exclude_index=0):
        headers = self.get_column_headers()
        self.initial_header_order = self.get_column_header_names()
        if len(headers) <= exclude_index + 3:
            raise Exception("Not enough columns to perform drag-and-drop.")
        indices = list(range(exclude_index + 1, len(headers)))
        random.shuffle(indices)
        src_idx, tgt_idx = indices[0], indices[1]
        source_elem = headers[src_idx]
        target_elem = headers[tgt_idx]
        source_name = source_elem.text.strip()
        target_name = target_elem.text.strip()
        # Scroll before dragging
        self.driver.execute_script("arguments[0].scrollIntoView(true);", source_elem)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", target_elem)
        print(f"Dragging '{source_name}' to '{target_name}'")
        old_order = self.get_column_header_names()
        print("Old order:", old_order)
        # Perform drag
        self.drag_and_drop_column(source_elem, target_elem)
        self.wait_for_header_order_change(old_order)
        new_order = self.get_column_header_names()
        return source_name, target_name, new_order

    # def sort_by_column_index(self, index, direction="asc"):
    #     """
    #     Click the header at position `index` (1-based) until it’s sorted as requested.
    #     direction: "asc", "desc", or "none"
    #     """
    #     headers = self.wait_for_all_elements(self.TABLE_HEADING_LABEL_LOCATOR)
    #     if index < 1 or index > len(headers):
    #         raise IndexError(f"Header index {index} out of range (1–{len(headers)})")
    #     header = headers[index - 1]
    #
    #     # What class name are we looking for?
    #     sort_class_map = {
    #         "asc": "ag-header-cell-sorted-asc",
    #         "desc": "ag-header-cell-sorted-desc",
    #         "none": "ag-header-cell-sorted-none"
    #     }
    #     expected_sort_class = sort_class_map[direction]
    #     # Find the .ag-cell-label-container under the header
    #     sort_container_xpath = f"(//div[contains(@class,'ag-header-cell')])[{index}]//div[contains(@class, 'ag-cell-label-container')]"
    #     for _ in range(3):  # AG-Grid cycles: none -> asc -> desc -> none..., so 3 clicks max
    #         self.driver.execute_script("arguments[0].click()", header)
    #         try:
    #             self.wait.until(
    #                 lambda d: expected_sort_class in d.find_element(By.XPATH, sort_container_xpath).get_attribute(
    #                     "class")
    #             )
    #             return self
    #         except Exception:
    #             continue
    #     raise Exception(f"Failed to sort column at index {index} to {direction}")

    # def get_column_values_by_index(self, index):
    #     """
    #     Return a list of values from the column at position `index` (1-based).
    #     """
    #     # Find every row’s cell in that column
    #     cells = self.driver.find_elements(
    #         By.XPATH,
    #         f"//div[contains(@class,'ag-center-cols-container')]//div[@role='gridcell'][{index}]"
    #     )
    #     return [cell.text.strip() for cell in cells]

    def sort_by_column_index(self, idx, direction):  # idx: 1-based
        sort_class = f"ag-header-cell-sorted-{direction}"  # "ag-header-cell-sorted-asc" or "desc"
        sort_header_xpath = f"(//div[contains(@class, 'ag-cell-label-container')])[{idx}]"
        sort_label_xpath =  f"(//div[contains(@class, 'ag-header-cell-comp-wrapper')])[{idx}]//div[@role='presentation']"
        header = self.driver.find_element(By.XPATH, sort_header_xpath)
        clicks = 0
        for _ in range(3):  # AG-Grid cycles: none -> asc -> desc -> none
            header.click()
            clicks += 1
            # Defensive wait—refresh element after click
            label = self.driver.find_element(By.XPATH, sort_label_xpath)
            if sort_class in label.get_attribute("class"):
                return clicks
        raise Exception(f"Could not sort column {idx} to {direction}")

    def get_column_values_by_index(self, col_idx):
        # Always get new elements after sorts/filters
        cell_xpath = f"//div[contains(@class,'ag-center-cols-container')]//div[@role='gridcell'][{col_idx}]"
        # Use explicit wait to avoid race between sort completion & query
        self.wait.until(
            lambda d: len(d.find_elements(By.XPATH, cell_xpath)) > 0
        )
        # Now fetch cells anew
        cells = self.driver.find_elements(By.XPATH, cell_xpath)
        return [cell.text.strip() for cell in cells]













import random
from operator import index
from typing import List

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
    DROP_WRAPPER_XPATH = "//div[contains(@class,'ag-column-drop-wrapper')]"
    HEADER_CELL_BY_INDEX = "(//div[contains(@class,'ag-cell-label-container')])[{idx}]"
    HEADER_TEXT_WITHIN_CELL='//span[@ref="eText" and @class="ag-header-cell-text"]'
    CENTER_VIEWPORT = "//div[contains(@class,'ag-center-cols-viewport')]"
    GROUP_FILTER_CANCEL_LOCATOR=(By.XPATH,"//span[contains(@class,'ag-column-drop-horizontal-cell-button') and @ref='eButton']//span[@unselectable='on']")
    DEFAULT_VIEW_LOCATOR=(By.XPATH,"//div[@class='ant-select ant-select-sm ant-select-filled css-cfjgob ant-select-single ant-select-show-arrow']//div[@class='ant-select-selector']")
    DROPDOWN_CONTAINER_LOCATOR=(By.XPATH,"//div[contains(@class,'ant-select-item-option-content') and not(contains(@class,'ant-select-dropdown-hidden'))]")
    VIEW_TO_BE_SELECTED_LOCATOR=(By.XPATH,"(//div[contains(@class,'ant-select-item-option-content') and not(contains(@class,'ant-select-dropdown-hidden'))])[2]")
    TEXT_TO_RETRIEVE_AFTER_VIEW_SELECTION_LOCATOR=(By.XPATH,"(//div[contains(@class,'ant-select')]//span[@class='ant-select-selection-item'])[1]")
    ELLIPSIS_SVG_LOCATOR_1=(By.XPATH,"(//div[contains(@class,'HeaderRight')]//*[name()='svg' and @data-icon='ellipsis'])[1]")
    ELLIPSIS_SVG_LOCATOR_2=(By.XPATH,"(//div[contains(@class,'HeaderRight')]//*[name()='svg' and @data-icon='ellipsis'])[3]")
    ELLIPSIS_SVG_LOCATOR_3=(By.XPATH,"(//div[contains(@class,'HeaderRight')]//*[name()='svg' and @data-icon='ellipsis'])[2]")
    DOWNLOAD_HISTORY_LOCATOR_1=(By.XPATH,"//span[contains(@class,'ant-dropdown') and normalize-space()='Download History']")
    DOWNLOAD_HISTORY_LOCATOR_2=(By.XPATH,"//div[@class='ant-dropdown css-cfjgob ant-dropdown-placement-bottomRight']//span[@class='ant-dropdown-menu-title-content'][normalize-space()='Download History']")
    DOWNLOAD_HISTORY_LOCATOR_3=(By.XPATH,"(//span[normalize-space()='Reports Export History'])[1]")
    MODAL_BOX_LOCATOR=(By.XPATH,'//div[contains(@class,"ant-modal-content")]//div[normalize-space()="Bulk Download History"]')
    RECORD_CONFIRMATION_LOCATOR=(By.XPATH,'(//div[@col-id="report_name"])[2]')
    MODAL_CLOSE_BUTTON_LOCATOR=(By.XPATH,'(//span[contains(@class,"anticon-close")])[2]')
    MODAL_MASK = (By.XPATH, "//div[contains(@class,'ant-modal-root')]//div[contains(@class,'ant-modal-mask') and not(contains(@class,'display: none'))]")
    FIRST_ROW_OF_TABLE_LOCATOR=(By.XPATH,'//div[@row-index="0"]//div[contains(@class,"ag-cell")]')
    TABLE_ROWS_LOCATOR=(By.XPATH, '//div[@role="row" and @row-index]')
    DESELECT_ALL_COLUMNS_LOCATOR=(By.XPATH,"(//div[contains(@role,'presentation')])[81]")
    HEADER_SELECTION_TEXTBOX_LOCATOR=(By.XPATH,"//div[contains(@class,'ag-column-select')]//input[@aria-label='Filter Columns Input' and @type='text']")
    FIRST_CHECKBOX_LOCATOR=(By.XPATH,"//div[contains(@class,'ag-column-select')]//div[contains(@class,'ag-column-select-column')]//span[contains(@class,'ag-column-select-column-label')]")
    CONTEXT_MENU_FOR_GROUPING_LOCATOR=(By.XPATH,"(//div[contains(@class,'ag-menu') or contains(@role,'menu')]//span[contains(@class,'ag-menu-option-text')])[2]")
    FIRST_COLUMN_ROW_LOCATOR=(By.XPATH,"//div[contains(@class,'ag-column-select')]//div[contains(@class,'ag-column-select-column')]")
    # Auto-group cues/classes can vary; we check any of these markers within first col cell
    AUTO_GROUP_MARKERS_XPATH = (
        "//*[contains(@class,'ag-group-expanded') or "
        "contains(@class,'ag-group-contracted') or "
        "contains(@class,'ag-group-value')]"
    )


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

    def _wait_for_drop_zone(self):
        return self.wait.until(EC.presence_of_element_located((By.XPATH, self.DROP_WRAPPER_XPATH)))

    def _get_header_el_by_index(self, idx: int):
        xpath = self.HEADER_CELL_BY_INDEX.format(idx=idx)
        return self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))

    def _scroll_header_into_view(self, header_el):
        try:
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'nearest', inline:'center'});",
                header_el
            )
        except Exception:
            pass

    def _get_header_text_by_index(self, idx: int) -> str:
        container_xpath = self.HEADER_CELL_BY_INDEX.format(idx=idx)
        label_xpath = f"{container_xpath}{self.HEADER_TEXT_WITHIN_CELL}"
        el = self.wait.until(EC.presence_of_element_located((By.XPATH, label_xpath)))
        return (el.text or "").strip()

    def get_group_chip_xpath_for_text(self, text: str) -> str:
        return (
            f"(//span[contains(@class,'ag-column-drop-horizontal-cell') and normalize-space()='{text}'])[2]"
        )

        # ---------- Public API ----------

    def drag_header_to_group_zone_by_index(self, idx: int) -> str:
        """
        Drag a header (by 1-based index) into the group drop zone.
        Returns the header text found at that index (can be empty if no label).
        """
        drop_zone = self._wait_for_drop_zone()
        header = self._get_header_el_by_index(idx)
        self._scroll_header_into_view(header)
        header_text = self._get_header_text_by_index(idx)

        actions = ActionChains(self.driver)
        # Robust drag and drop sequence
        actions.move_to_element(header).click_and_hold().pause(0.2) \
            .move_to_element(drop_zone).pause(0.2).release().perform()

        # Verify a chip appears. If header text is blank (icon columns), we fall back to any chip presence.
        print(header_text)
        if header_text:
            chip_xpath = self.get_group_chip_xpath_for_text(header_text)
            self.wait.until(EC.presence_of_element_located((By.XPATH, chip_xpath)))
        else:
            # Fallback: any chip appeared in drop wrapper
            self.wait.until(EC.presence_of_element_located((
                By.XPATH,
                f"{self.DROP_WRAPPER_XPATH}//div[contains(@class,'ag-column-drop-cell')]"
            )))
        return header_text

    def drag_headers_to_group_zone_by_indices(self, indices: List[int]) -> List[str]:
        names = []
        for idx in indices:
            name = self.drag_header_to_group_zone_by_index(idx)
            names.append(name)
        return names

    def get_grouped_chip_texts(self):
        time.sleep(10)
        elements = self.driver.find_elements(
            By.XPATH,
            "//span[contains(@class,'ag-column-drop-horizontal-cell')]"
        )

        chip_texts = self.driver.execute_script("""
            return arguments[0].map(el => el.textContent.trim());
        """, elements)
        print(chip_texts)
        return chip_texts

    def is_auto_group_column_present_left(self) -> bool:
        """
        Detect the presence of the Auto Group column at the left (index 1)
        by finding group markers inside first column cells.
        """
        # Find any row, first column cell, then look for group markers in it
        time.sleep(5)
        first_col_cells = self.driver.find_elements(
            By.XPATH,
            "//div[contains(@class,'ag-center-cols-container')]//div[@role='row']//div[@role='gridcell'][1]"
        )
        if first_col_cells:
                return True
        return False

    def expand_first_group_if_collapsed(self):
        """
        Optional: Expand the first group if a collapsed icon is found to validate group rows existence.
        """
        collapsed_icons = self.driver.find_elements(
            By.XPATH,
            "//span[contains(@class,'ag-group-contracted')]"
        )
        if collapsed_icons:
            try:
                collapsed_icons[0].click()
            except Exception:
                pass

    def has_group_rows(self) -> bool:
        """
        Check for group rows existence via common group row classes.
        """
        group_rows = self.driver.find_elements(
            By.XPATH,
            "//*[contains(@class,'ag-group-row') or contains(@class,'ag-row-group')]"
        )
        return len(group_rows) > 0

    def clear_grouping(self):
        """
        Click 'x' on each chip in the drop zone (if present) to clear grouping.
        """
        btn=self.visible_element(self.GROUP_FILTER_CANCEL_LOCATOR)
        try:
            btn.click()
        except Exception:
            pass


    def switch_to_different_view(self):
        time.sleep(2)
        self.visible_element(self.DEFAULT_VIEW_LOCATOR).click()
        self.visible_element(self.DROPDOWN_CONTAINER_LOCATOR)
        label_name_dropdown_to_be_selected=self.visible_text(self.VIEW_TO_BE_SELECTED_LOCATOR)
        self.visible_element(self.VIEW_TO_BE_SELECTED_LOCATOR).click()
        label_name_of_view = self.visible_text(self.TEXT_TO_RETRIEVE_AFTER_VIEW_SELECTION_LOCATOR)
        return label_name_of_view,label_name_dropdown_to_be_selected

    def get_download_history_downloads(self):
        self.click(self.ELLIPSIS_SVG_LOCATOR_1)
        self.click(self.DOWNLOAD_HISTORY_LOCATOR_1)
        self.visible_element(self.MODAL_BOX_LOCATOR)
        report_name=self.visible_text(self.RECORD_CONFIRMATION_LOCATOR)
        self.driver.switch_to.active_element.send_keys(Keys.ESCAPE)
        self.invisible_element(self.MODAL_BOX_LOCATOR)
        if report_name:
            return True
        else:
            return False

    def get_upload_history_downloads(self):
        self.click(self.ELLIPSIS_SVG_LOCATOR_2)
        self.click(self.DOWNLOAD_HISTORY_LOCATOR_2)
        self.visible_element(self.MODAL_BOX_LOCATOR)
        report_name=self.visible_text(self.RECORD_CONFIRMATION_LOCATOR)
        self.driver.switch_to.active_element.send_keys(Keys.ESCAPE)
        self.invisible_element(self.MODAL_BOX_LOCATOR)
        if report_name:
            return True
        else:
            return False

    def get_report_history_downloads(self):
        self.click(self.ELLIPSIS_SVG_LOCATOR_3)
        self.click(self.DOWNLOAD_HISTORY_LOCATOR_3)
        self.visible_element(self.MODAL_BOX_LOCATOR)
        report_name = self.visible_text(self.RECORD_CONFIRMATION_LOCATOR)
        self.driver.switch_to.active_element.send_keys(Keys.ESCAPE)
        self.invisible_element(self.MODAL_BOX_LOCATOR)
        if report_name:
            return True
        else:
            return False



    def validate_table_has_data(self):
        """Comprehensive table data validation"""
        try:
            # Check if table has rows
            all_rows = self.wait_for_all_elements(self.TABLE_ROWS_LOCATOR)
            if not all_rows:
                return False, "No data rows found in table"
            # Check first row specifically
            first_row_cells =self.wait_for_all_elements(self.FIRST_ROW_OF_TABLE_LOCATOR)
            if not first_row_cells:
                return False, "No cells found in first row"
            # Validate cell content
            non_empty_cells = 0
            cell_data = {}

            for cell in first_row_cells:
                col_id = cell.get_attribute("col-id")
                cell_text = cell.text.strip()

                if cell_text and cell_text != "-" and cell_text != "":
                    non_empty_cells += 1
                    cell_data[col_id] = cell_text

            if non_empty_cells < 3:
                return False, f"Insufficient data: only {non_empty_cells} non-empty cells"

            return True, {
                "total_cells": len(first_row_cells),
                "non_empty_cells": non_empty_cells,
                "sample_data": dict(list(cell_data.items())[:3])  # First 3 entries
            }

        except Exception as e:
            return False, f"Table validation error: {str(e)}"

    def no_of_table_header_after_deselection(self):
        time.sleep(2)
        self.click(self.DESELECT_ALL_COLUMNS_LOCATOR)
        no_of_header=len(self.driver.find_elements(*self.TABLE_HEADING_LABEL_LOCATOR))
        if no_of_header <= 2:
            return True
        else:
            return False


    def enter_text_into_textbox_for_column_header_selection(self):
        self.click(self.DESELECT_ALL_COLUMNS_LOCATOR)
        self.enter_text(self.HEADER_SELECTION_TEXTBOX_LOCATOR,"amount")
        # self.visible_element(self.FIRST_CHECKBOX_LOCATOR)
        self.visible_element(self.FIRST_CHECKBOX_LOCATOR).click()
        headers=self.wait_for_all_elements(self.TABLE_HEADING_LABEL_LOCATOR)
        no_of_headers=len(headers)
        if no_of_headers == 3:
            return True
        else:
            return False

    def aggregate_function_to_column(self):
        column=self.visible_element(self.FIRST_COLUMN_ROW_LOCATOR)
        time.sleep(1)
        actions = ActionChains(self.driver)
        actions.move_to_element(column).context_click(column).perform()
        time.sleep(5)
        self.click(self.CONTEXT_MENU_FOR_GROUPING_LOCATOR)
        time.sleep(10)


























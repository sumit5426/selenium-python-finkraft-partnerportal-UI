import time

from selenium.webdriver.support import expected_conditions as EC

from selenium.common import StaleElementReferenceException, ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from utils.browser_utility import BrowserUtility


class CredentialsPage(BrowserUtility):
    def __init__(self, driver):
        super().__init__(driver)

    TOP_MODULE_CRED_BUTTON_LOCATOR=(By.XPATH,'//div[@class="ant-tabs-tab-btn"]')
    ALL_INTEGRATION_BUTTON_LOCATOR=(By.XPATH,"//div[@id='rc-tabs-3-tab-1']")
    SEARCH_BAR_LOCATOR=(By.XPATH,"//span[@class='ant-input-affix-wrapper css-cfjgob ant-input-outlined']")
    CARD_LOCATOR=(By.CSS_SELECTOR,".IntegrationCard")
    CARD_LABEL_NAME_LOCATOR=(By.XPATH,'//h2[@class="headerTextGST"]')
    TABLE_HEADING_LABEL_LOCATOR=(By.XPATH,'//span[@ref="eText" and @class="ag-header-cell-text"]')
    GST_BUTTON_LOCATOR=(By.XPATH,'(//div[@class="ant-tabs-tab-btn"])[2]')
    AIRLINE_BUTTON_LOCATOR = (By.XPATH, '(//div[@class="ant-tabs-tab-btn"])[3]')
    EMAIL_BUTTON_LOCATOR = (By.XPATH, '(//div[@class="ant-tabs-tab-btn"])[4]')
    NO_ACTION_REQUIRED_TAB_LOCATOR = (By.XPATH, '//div[@title="No Action Required"]')
    TOGGLE_BUTTONS_LOCATOR = (By.XPATH, '//button[@ref="eToggleButton"]')
    CHECKBOXES_LOCATOR = (By.XPATH, '//input[contains(@aria-label,"Press SPACE to toggle visibility")]')
    CHECKBOX_LABELS_LOCATOR = (By.XPATH, '//span[@class="ag-column-select-column-label"]')





    def click_take_action_button(self):
        print("click_take_action_button")
        options=self.wait_for_all_elements(self.TOP_MODULE_CRED_BUTTON_LOCATOR)
        print("options=", options)
        for index, option in enumerate(options):
            if index == 0:
                continue
            try:
                self.is_element_present(self.ALL_INTEGRATION_BUTTON_LOCATOR)
                self.wait.until(EC.element_to_be_clickable(
                    (By.XPATH, f"({self.TOP_MODULE_CRED_BUTTON_LOCATOR[1]})[{index + 1}]"))).click()
                print(f"Clicked option {index + 1}")
                self.visible_element(self.SEARCH_BAR_LOCATOR)
            except (StaleElementReferenceException, ElementClickInterceptedException) as e:
                print(f"Click failed for index {index + 1}: {type(e).__name__}")

    def get_integration_cards(self):
        """Returns a list of WebElements for all integration cards."""
        return self.wait_for_all_elements(self.CARD_LOCATOR)

    def get_card_labels(self):
        """Returns a list of label texts for all cards with the given header class."""
        elements = self.wait_for_all_elements(self.CARD_LABEL_NAME_LOCATOR)
        return [el.text.strip() for el in elements]

    def get_gst_ag_grid_table_headings(self):
        """Returns a list of AG Grid table heading texts."""
        self.click(self.GST_BUTTON_LOCATOR)
        elements = self.wait_for_all_elements(self.TABLE_HEADING_LABEL_LOCATOR)
        if not elements:
            return []  # No
        return [el.text.strip() for el in elements[:6]]

    def click_no_action_required_gst_tab(self):
        """Returns a list of AG Grid table heading texts."""
        self.click(self.NO_ACTION_REQUIRED_TAB_LOCATOR)
        elements = self.wait_for_all_elements(self.TABLE_HEADING_LABEL_LOCATOR)
        if not elements:
            return []
        return [el.text.strip() for el in elements[:6]]

    def get_airline_ag_grid_table_headings(self):
        """Returns a list of AG Grid table heading texts."""
        self.click(self.AIRLINE_BUTTON_LOCATOR)
        elements = self.wait_for_all_elements(self.TABLE_HEADING_LABEL_LOCATOR)
        if not elements:
            return []
        return [el.text.strip() for el in elements[:7]]

    def click_no_action_required_airline_tab(self):
        """Returns a list of AG Grid table heading texts."""
        self.click(self.NO_ACTION_REQUIRED_TAB_LOCATOR)
        elements = self.wait_for_all_elements(self.TABLE_HEADING_LABEL_LOCATOR)
        if not elements:
            return []
        return [el.text.strip() for el in elements[:7]]


    def get_email_ag_grid_table_headings(self):
        """Returns a list of AG Grid table heading texts."""
        self.click(self.EMAIL_BUTTON_LOCATOR)
        self.wait_for_all_elements(self.TABLE_HEADING_LABEL_LOCATOR)
        elements = self.driver.find_elements(*self.TABLE_HEADING_LABEL_LOCATOR)
        if not elements:
            return []
        return [el.text.strip() for el in elements[:6]]

    def click_no_action_required_email_tab(self):
        """Returns a list of AG Grid table heading texts."""
        self.click(self.NO_ACTION_REQUIRED_TAB_LOCATOR)
        self.wait_for_all_elements(self.TABLE_HEADING_LABEL_LOCATOR)
        elements = self.wait_for_all_elements(self.TABLE_HEADING_LABEL_LOCATOR)
        if not elements:
            return []
        return [el.text.strip() for el in elements[:6]]

    def select_module(self, module):
        if module == "gst":
            self.click(self.GST_BUTTON_LOCATOR)
        elif module == "airline":
            self.click(self.AIRLINE_BUTTON_LOCATOR)
        elif module == "email":
            self.click(self.EMAIL_BUTTON_LOCATOR)
        else:
            raise ValueError(f"Unknown module: {module}")

    def has_table_headings(self):
        elements = self.driver.find_elements(*self.TABLE_HEADING_LABEL_LOCATOR)
        return len(elements) > 0

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

    def open_column_selector(self, toggle_index=0):
        buttons = self.wait_for_all_elements(self.TOGGLE_BUTTONS_LOCATOR)
        buttons[toggle_index].click()
        # Optionally, wait for checkboxes to appear
        self.wait_for_all_elements(self.CHECKBOXES_LOCATOR)

    def get_column_checkboxes(self):
        return self.driver.find_elements(*self.CHECKBOXES_LOCATOR)

    def get_checkbox_labels(self):
        return [el.text.strip() for el in self.driver.find_elements(*self.CHECKBOX_LABELS_LOCATOR)]

    def get_table_headings(self):
        return [el.text.strip() for el in self.driver.find_elements(*self.TABLE_HEADING_LABEL_LOCATOR)]

    def toggle_checkbox_and_wait(self, checkbox, expected_visible, timeout=5):
        aria_label = checkbox.get_attribute("aria-label")
        is_selected = "visible" in aria_label
        # Click to change state
        checkbox.click()
        # Wait for aria-label to update
        expected_str = "visible" if expected_visible else "hidden"
        WebDriverWait(self.driver, timeout).until(
            lambda d: expected_str in checkbox.get_attribute("aria-label"),
            message=f"aria-label did not become {expected_str} after clicking"
        )















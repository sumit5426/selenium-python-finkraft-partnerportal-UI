import time

from selenium.webdriver.support import expected_conditions as EC

from selenium.common import StaleElementReferenceException, ElementClickInterceptedException
from selenium.webdriver.common.by import By

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
        return [el.text.strip() for el in elements[:6]]

    def get_airline_ag_grid_table_headings(self):
        """Returns a list of AG Grid table heading texts."""
        self.click(self.AIRLINE_BUTTON_LOCATOR)
        elements = self.wait_for_all_elements(self.TABLE_HEADING_LABEL_LOCATOR)
        return [el.text.strip() for el in elements[:7]]










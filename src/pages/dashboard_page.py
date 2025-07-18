import time

from selenium.common import ElementClickInterceptedException, ElementNotInteractableException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from conftest import driver
from pages.credentials_page import CredentialsPage
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
    TOP_SUB_MODULE_LOCATOR = (By.XPATH, '//div[@class="ant-tabs-tab-btn"]')
    MODULE_CONTENT_LOCATOR = (By.CSS_SELECTOR, ".module-content")
    SET_VIEW_TITLE_LOCATOR = (By.CSS_SELECTOR, "#setViewTitle")
    total_trans = (By.XPATH, '(//div[@refelname="dArea"]//div[@zdbname="datacell"]//span[@zdbname="dataspan"])[2]')
    checkbox = (By.XPATH, '(//li[contains(@class, "zdropdownlist__item")]//input[@type="checkbox"])[2]')
    OK_BUTTON_LOCATOR = (By.XPATH, '//button[@aria-label="OK"]')
    checkbox_final = (By.XPATH,
                      "(//li[contains(@class, 'zdropdownlist__item') and contains(@class, 'is-selected')]//div[contains(@class, 'zdropdownlist__checkbox')])[1]")
    checkbox_final2 = (By.XPATH,
                       "(//li[contains(@class, 'zdropdownlist__item') and contains(@class, 'is-selected')]//div[contains(@class, 'zdropdownlist__checkbox')])[1]")
    ALL_DROPDOWNS = (By.XPATH, "//div[@class='ZR-DashboardUFContainer']//div[@elname='filterHead']")
    CUSTOM_OPTIONS = (By.XPATH, '//span[@class="zdropdownlist__text"]')
    CALENDAR_LOCATOR=(By.XPATH, '//input[contains(@class,"mcLoaded")]')
    RESET_BUTTON_LOCATOR=(By.XPATH,"//div[@class='dFilterHolder']//div[@class='vmfResetButton']")
    SUB_SUB_MODULE_LOCATOR=(By.XPATH,'//div[@elname="tabHeaderDivInput"]')
    CREDENTIALS_MODULE_LOCATOR=(By.XPATH,"//p[normalize-space()='Credentials']")

    WIDGET_LOCATORS = {
        "logo": {
            "locator": (By.XPATH, "//img[@alt='appIcon']"),
            "in_iframe": False
        },
        # "piechart": {
        #     "locator": (By.CSS_SELECTOR, ".piegroup"),
        #     "in_iframe": True
        # },
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
        workspace_switch_locator=(By.XPATH, f"//p[normalize-space()='{workspace_name}']")
        self.click_scroll(workspace_switch_locator)
        return self.visible_text(workspace_switch_locator)

    def is_widget_visible(self, widget_name, timeout=10):
        widget_info = self.WIDGET_LOCATORS.get(widget_name)
        if not widget_info:
            logger.warning(f"No locator defined for widget: {widget_name}")
            return False
        locator = widget_info["locator"]
        in_iframe = widget_info.get("in_iframe", False)
        try:
            if in_iframe:
                self.switch_to_iframe(self.IFRAME_LOCATOR)
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


    def are_modules_present(self, expected_modules: list[str]) -> list[str]:
        """Returns the list of modules from expected_modules that are missing from UI."""
        elements = self.driver.find_elements(*self.MODULE_LIST_LOCATOR)
        visible_modules = self.get_visible_modules_texts(elements)
        missing = [mod for mod in expected_modules if mod not in visible_modules]
        return missing

    def get_top_horizontal_modules(self):
        elements = self.driver.find_elements(*self.TOP_SUB_MODULE_LOCATOR)
        return [ el.text.strip().lower() for el in elements if el.is_displayed() and el.text.strip() ]

    def are_top_modules_present(self, expected_keywords: list[str]) -> list[str]:
        actual_modules = self.get_top_horizontal_modules()
        print("actual module"+str(actual_modules))# e.g., ['dashboard-hotel', 'airline']
        missing = []
        for keyword in expected_keywords:
            if not any(keyword.lower() in mod for mod in actual_modules): missing.append(keyword)
        return missing

    def click_top_module(self, module_name: str):
        modules = self.driver.find_elements(*self.TOP_SUB_MODULE_LOCATOR)
        print("module"+str(modules))
        for module in modules:
            if module.is_displayed() and module_name.lower() in module.text.lower():
                module.click()
                return True
        raise Exception(f"Module '{module_name}' not found or not clickable.")


    def is_module_data_loaded(self):
        content = self.visible_element(self.MODULE_CONTENT_LOCATOR)
        if content:
            return content.is_displayed()
        return False


    def get_module_title_text(self):
        element = self.visible_element(self.SET_VIEW_TITLE_LOCATOR)
        return element.text if element else None

    def switch_to_dashboard_iframe(self):
        self.switch_to_iframe(self.IFRAME_LOCATOR)

    def switch_to_default(self):
        self.switch_to_default_content()
        print("[switch_to_default] Switched back to main content.")

    def validate_all_dropdowns_have_values(self):
        time.sleep(5)  # Optional wait
        result = []
        top_modules = self.driver.find_elements(*self.TOP_SUB_MODULE_LOCATOR)
        print("Top modules found:", len(top_modules))
        for module_index, module in enumerate(top_modules):
            try:
                self.switch_to_default_content()
                module.click()
                time.sleep(1)
                self.switch_to_dashboard_iframe()
                sub_sub_modules = self.driver.find_elements(*self.SUB_SUB_MODULE_LOCATOR)
                print(f"Module {module_index + 1}: Sub-sub-modules found: {len(sub_sub_modules)}")

                if len(sub_sub_modules) > 1:
                    for sub_index, sub_module in enumerate(sub_sub_modules):
                        try:
                            sub_module.click()
                            time.sleep(1)
                            dropdowns = self.driver.find_elements(*self.ALL_DROPDOWNS)
                            print(f"Sub-sub-module {sub_index + 1}: Dropdowns found: {len(dropdowns)}")
                            for dropdown_index, dropdown in enumerate(dropdowns):
                                try:
                                    self.scroll_into_view(dropdown)
                                    time.sleep(1)
                                    class_attr = dropdown.get_attribute("class")
                                    if "dataRangeHolder" in class_attr:
                                        print(f"[ℹ️] Dropdown {dropdown_index + 1} is a calendar. Skipping.")
                                        continue
                                    dropdown.click()
                                    options = self.wait_for_all_elements(self.CUSTOM_OPTIONS)
                                    visible_options = [opt for opt in options if
                                                       opt.is_displayed() and opt.text.strip()]
                                    dropdown.click()  # Close the dropdown
                                    result.append({
                                        "module": module_index + 1,
                                        "sub_sub_module": sub_index + 1,
                                        "dropdown_index": dropdown_index,
                                        "has_value": len(visible_options) > 0
                                    })
                                except Exception as e:
                                    print(f"[Dropdown {dropdown_index}] Exception: {e}")
                        except Exception as e:
                            print(f"[Sub-sub-module {sub_index}] Exception: {e}")
                else:
                    # No sub-sub-module, directly validate dropdowns
                    dropdowns = self.driver.find_elements(*self.ALL_DROPDOWNS)
                    print(f"No sub-sub-modules: Dropdowns found: {len(dropdowns)}")

                    for dropdown_index, dropdown in enumerate(dropdowns):
                        try:
                            self.scroll_into_view(dropdown)
                            class_attr = dropdown.get_attribute("class")
                            if "dataRangeHolder" in class_attr:
                                print(f"[ℹ️] Dropdown {dropdown_index + 1} is a calendar. Skipping.")
                                continue
                            dropdown.click()
                            options = self.wait_for_all_elements(self.CUSTOM_OPTIONS)
                            visible_options = [opt for opt in options if opt.is_displayed() and opt.text.strip()]
                            dropdown.click()  # Close the dropdown
                            result.append({
                                "module": module_index + 1,
                                "dropdown_index": dropdown_index,
                                "has_value": len(visible_options) > 0
                            })
                        except Exception as e:
                            print(f"[Dropdown {dropdown_index}] Exception: {e}")
                    self.switch_to_default_content()
            except Exception as e:
                print(f"[Module {module_index + 1}] Exception: {e}")

        print(result)
        return result

    def validate_all_dropdowns_functionality(self):
        # self.switch_to_iframe(self.IFRAME_LOCATOR)
        self.to_open_iframe_cors_in_another_tab(self.IFRAME_LOCATOR)
        self.driver.execute_script("document.querySelector('.scrollFreeze')?.remove();")
        print("[validate_all_dropdowns_have_values]")
        dropdowns = self.driver.find_elements(*self.ALL_DROPDOWNS)
        print(f"Found {len(dropdowns)} dropdowns")
        if not dropdowns:
            print("ℹ️ No dropdowns found on this portal — skipping dropdown validation.")
            return
        unchanged_dropdowns = []
        error_dropdowns = []
        changed_dropdowns = []
        time.sleep(5)
        for index, dropdown in enumerate(dropdowns):
            try:
                time.sleep(2)
                self.scroll_into_view(dropdown)
                self.driver.execute_script("document.querySelector('#ZRSTipPointer')?.remove();")
                time.sleep(2)
                class_attr = dropdown.get_attribute("class")
                print(f"dropdown class attribute: {class_attr}")
                if "dataRangeHolder" in class_attr:
                    print(f"[ℹ️] Dropdown {index + 1} is a calendar. Skipping.")
                    continue
                dropdown.click()
                print(f"Dropdown {index + 1} clicked")
                # if self.is_element_present(self.CALENDAR_LOCATOR):
                #     print(f"[ℹ️] Dropdown {index + 1} is a calendar. Skipping.")
                #     continue
                options = self.wait_for_all_elements(self.CUSTOM_OPTIONS)
                print(f"Dropdown {index + 1} has {len(options)} options")
                if len(options) > 2:
                    before_value = self.visible_text(self.total_trans)
                    # Always click the second option
                    second_option = options[1]
                    self.scroll_into_view(second_option)
                    second_option.click()
                    print(f"Clicked second option (index 1) in dropdown {index + 1}")

                    ok_clicked = False
                    try:
                        time.sleep(1)
                        ok_button_elem = self.visible_element(self.OK_BUTTON_LOCATOR)
                        if ok_button_elem:
                            classes = ok_button_elem.get_attribute("class")
                            is_disabled_attr = ok_button_elem.get_attribute("disabled")
                            aria_disabled = ok_button_elem.get_attribute("aria-disabled")
                            if (
                                "is-disabled" not in classes
                                and not is_disabled_attr
                                and aria_disabled != "true"
                            ):
                                self.scroll_into_view(ok_button_elem)
                                self.driver.execute_script("document.querySelector('#ZRSTipPointer')?.remove();")
                                ok_button_elem.click()
                                ok_clicked = True
                                print(f"OK button clicked after selecting second option (confirmed enabled)")
                            else:
                                print(f"OK button is disabled after selecting second option, will try third option")
                        else:
                            print(f"OK button not found after selecting second option")
                    except Exception as e:
                        print(f"[⚠️] Exception after clicking second option: {e}")

                    # If OK not clicked, try third option and check again
                    if not ok_clicked and len(options) > 2:
                        third_option = options[2]
                        self.scroll_into_view(third_option)
                        self.driver.execute_script("document.querySelector('#ZRSTipPointer')?.remove();")
                        third_option.click()
                        print(f"Clicked third option (index 2) in dropdown {index + 1} (from exception handler or disabled OK)")
                        try:
                            time.sleep(1)
                            ok_button_elem = self.visible_element(self.OK_BUTTON_LOCATOR)
                            if ok_button_elem:
                                classes = ok_button_elem.get_attribute("class")
                                is_disabled_attr = ok_button_elem.get_attribute("disabled")
                                aria_disabled = ok_button_elem.get_attribute("aria-disabled")
                                if (
                                    "is-disabled" not in classes
                                    and not is_disabled_attr
                                    and aria_disabled != "true"
                                ):
                                    self.scroll_into_view(ok_button_elem)
                                    ok_button_elem.click()
                                    ok_clicked = True
                                    print(f"OK button clicked after selecting third option (confirmed enabled)")
                                else:
                                    print(f"OK button is still disabled after selecting third option")
                            else:
                                print(f"OK button not found after selecting third option")
                        except Exception as e2:
                            print(f"[❌] Even after clicking third option, OK button could not be clicked: {e2}")
                    elif not ok_clicked:
                        print(f"[⚠️] No third option to try in dropdown {index + 1}")

                    time.sleep(1)
                    after_value = self.visible_text(self.total_trans)
                    print(f"After Value for dropdown {index + 1}: {after_value}")

                    if before_value != after_value:
                        print(f"[✅] Value changed as expected for dropdown {index + 1}")
                        changed_dropdowns.append(f"Dropdown {index + 1}")

                    else:
                        # options = self.wait_for_all_elements(self.CUSTOM_OPTIONS)
                        print(f"[⚠️] Value not changed as expected for dropdown , trying for more one time   {index + 1}")
                        time.sleep(1)
                        self.scroll_into_view(dropdown)
                        dropdown.click()
                        third_option = options[2]
                        time.sleep(1)
                        self.scroll_into_view(third_option)
                        self.driver.execute_script("document.querySelector('#ZRSTipPointer')?.remove();")
                        third_option.click()
                        second_option.click()
                        self.visible_element(self.OK_BUTTON_LOCATOR)
                        ok_button_elem=self.driver.find_element(*self.OK_BUTTON_LOCATOR)
                        if ok_button_elem.is_enabled():
                            ok_button_elem.click()
                            print(f"clicked on button after clicking third option (confirmed enabled)")
                        after_value_2 = self.visible_text(self.total_trans)
                        if after_value_2 == before_value:
                            print(
                                f"[⚠️] Value still unchanged after second attempt — trying Reset button for dropdown {index + 1}")

                            try:
                                reset_button = self.visible_element(*self.RESET_BUTTON_LOCATOR)
                                self.scroll_into_view(reset_button)
                                reset_button.click()
                                print(f"[🔄] Clicked Reset button for dropdown {index + 1}")
                                self.wait_for_value_change(after_value_2, self.total_trans)
                                after_value_3 = self.visible_text(self.total_trans)
                                print(f"After Reset Value for dropdown {index + 1}: {after_value_3}")

                                if after_value_3 == after_value_2:
                                    print(f"[❌] Even after Reset, value not changed for dropdown {index + 1}")
                                    unchanged_dropdowns.append(f"Dropdown {index + 1}")
                                else:
                                    print(f"[✅] Value changed after Reset for dropdown {index + 1}")
                                    changed_dropdowns.append(f"Dropdown {index + 1} (after Reset)")

                            except Exception as e:
                                print(f"[❌] Failed to click Reset for dropdown {index + 1}: {e}")
                                unchanged_dropdowns.append(f"Dropdown {index + 1} - Reset failed")

                else:
                    print(f"[ℹ️] Skipping dropdown {index + 1} (only or two option)")

            except Exception as e:
                print(f"[❌] Error processing dropdown {index + 1}: {str(e)}")
                error_dropdowns.append(f"Dropdown {index + 1} - {str(e)}")
        return unchanged_dropdowns, error_dropdowns, changed_dropdowns

    def find_vertical_scrollable_elements(self,selector=".ly-lineWrapper"):
        self.to_open_iframe_cors_in_another_tab(self.IFRAME_LOCATOR)
        self.scroll_to_bottom_of_container(selector)

    def go_to_credentials(self):
        self.click(self.CREDENTIALS_MODULE_LOCATOR)
        credentials_page=CredentialsPage(self.driver)
        return credentials_page









    
















import time

from selenium.common import ElementClickInterceptedException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from conftest import driver
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
    TOP_SUB_MODULE_LOCATOR = (By.XPATH, '//div[@class="ant-tabs-tab-btn"]')  # Adjust as per your HTML

    WIDGET_LOCATORS = {
        "logo": {
            "locator": (By.XPATH, "//img[@alt='appIcon']"),
            "in_iframe": False
        },
        "piechart": {
            "locator": (By.CSS_SELECTOR, ".piegroup"),
            "in_iframe": True
        },
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
        WORKSPACE=(By.XPATH, f"//p[normalize-space()='{workspace_name}']")
        self.click_scroll(WORKSPACE)
        return self.visible_text(self.WORKSPACE_NAME)

    def switch_to_dashboard_iframe(self):
        iframe = self.driver.find_element(*self.IFRAME_LOCATOR)
        self.driver.switch_to.frame(iframe)

    def is_widget_visible(self, widget_name, timeout=10):
        widget_info = self.WIDGET_LOCATORS.get(widget_name)
        if not widget_info:
            logger.warning(f"No locator defined for widget: {widget_name}")
            return False
        locator = widget_info["locator"]
        in_iframe = widget_info.get("in_iframe", False)
        try:
            if in_iframe:
                self.switch_to_dashboard_iframe()
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

    def get_visible_modules(self):
        """Return a list of visible module names from sidebar."""
        elements = self.driver.find_elements(*self.MODULE_LIST_LOCATOR)
        self.visible_element()
        return [el.text.strip() for el in elements if el.is_displayed() and el.text.strip()]

    def are_modules_present(self, expected_modules: list[str]) -> list[str]:
        """Returns the list of modules from expected_modules that are missing from UI."""
        visible_modules = self.get_visible_modules()
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
        for module in modules:
            if module.is_displayed() and module_name.lower() in module.text.lower():
                module.click()
                return True
        raise Exception(f"Module '{module_name}' not found or not clickable.")

    MODULE_CONTENT_LOCATOR = (By.CSS_SELECTOR, ".module-content")  # adjust as per your DOM

    def is_module_data_loaded(self):
        content = self.visible_element(self.MODULE_CONTENT_LOCATOR)
        if content:
            return content.is_displayed()
        return False

    SET_VIEW_TITLE_LOCATOR = (By.CSS_SELECTOR, "#setViewTitle")

    def get_module_title_text(self):
        element = self.visible_element(self.SET_VIEW_TITLE_LOCATOR)
        return element.text if element else None

    # def switch_to_dashboard_iframe(self):
    #     try:
    #         # Adjust locator if needed
    #         iframe = self.visible_element((By.CSS_SELECTOR, "iframe"))
    #         self.driver.switch_to.frame(iframe)
    #         print("[switch_to_dashboard_iframe] Switched to dashboard iframe.")
    #     except Exception as e:
    #         raise Exception(f"Failed to switch to iframe: {e}")

    def switch_to_default(self):
        self.driver.switch_to.default_content()
        print("[switch_to_default] Switched back to main content.")

    ALL_DROPDOWNS = (By.XPATH, "//div[@class='ZR-DashboardUFContainer']//div[@elname='filterHead']")
    CUSTOM_OPTIONS = (By.XPATH, '//span[@class="zdropdownlist__text"]')

    def validate_all_dropdowns_have_values(self):
        result = []
        self.switch_to_dashboard_iframe()
        dropdowns = self.driver.find_elements(*self.ALL_DROPDOWNS)
        print(dropdowns)
        for index, dropdown in enumerate(dropdowns):
            has_value = False
            try:
                self.scroll_into_view(dropdown)
                dropdown.click()
                options = self.wait_for_all_elements(self.CUSTOM_OPTIONS)
                texts = [opt.text.strip() for opt in options if opt.text.strip()]

                # Print the list of non-empty option texts
                print(f"Dropdown has the following options: {texts}")
                visible_options = [opt for opt in options if opt.is_displayed() and opt.text.strip()]
                has_value = len(visible_options) > 0
                dropdown.click()  #
            except Exception as e:
                print(f"[Dropdown {index}] Exception: {e}")
            result.append({
                "dropdown_index": index,
                "has_value": has_value
            })
        self.switch_to_default()
        print(result)
        return result

    total_trans=(By.XPATH,'(//div[@refelname="dArea"]//div[@zdbname="datacell"]//span[@zdbname="dataspan"])[2]')
    checkbox = (By.XPATH, '(//li[contains(@class, "zdropdownlist__item")]//input[@type="checkbox"])[2]')
    ok_button = (By.XPATH, '//button[@aria-label="OK"]')
    checkbox_final=(By.XPATH, "(//li[contains(@class, 'zdropdownlist__item') and contains(@class, 'is-selected')]//div[contains(@class, 'zdropdownlist__checkbox')])[1]")
    checkbox_final2=(By.XPATH, "(//li[contains(@class, 'zdropdownlist__item') and contains(@class, 'is-selected')]//div[contains(@class, 'zdropdownlist__checkbox')])[1]")

    def validate_all_dropdowns_functionality(self):
        self.switch_to_dashboard_iframe()
        self.driver.execute_script("document.querySelector('.scrollFreeze')?.remove();")
        print("[validate_all_dropdowns_have_values]")
        dropdowns = self.driver.find_elements(*self.ALL_DROPDOWNS)
        print(f"Found {len(dropdowns)} dropdowns")
        if not dropdowns:
            print("ℹ️ No dropdowns found on this portal — skipping dropdown validation.")
            return  # Early exit, do not fail the test
        unchanged_dropdowns = []  # Dropdowns where value didn't change
        error_dropdowns = []  # Dropdowns where exception occurred
        time.sleep(5)
        for index, dropdown in enumerate(dropdowns):
            try:
                time.sleep(2)
                self.scroll_into_view(dropdown)
                self.driver.execute_script("document.querySelector('#ZRSTipPointer')?.remove();")
                time.sleep(2)
                dropdown.click()
                print(f"Dropdown {index + 1} clicked")
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
                        ok_button_elem = self.visible_element(self.ok_button)
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
                            ok_button_elem = self.visible_element(self.ok_button)
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

                    self.wait_for_value_change(before_value, self.total_trans)
                    after_value = self.visible_text(self.total_trans)
                    print(f"After Value for dropdown {index + 1}: {after_value}")

                    if before_value != after_value:
                        print(f"[✅] Value changed as expected for dropdown {index + 1}")
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
                        self.visible_element(self.ok_button).click()
                        self.wait_for_value_change(after_value, self.total_trans)
                        after_value_2 = self.visible_text(self.total_trans)
                        if after_value_2 == after_value:
                            print(f"[❌] Value not changed as expected for dropdown after retrying for dropdown {index + 1}")
                            unchanged_dropdowns.append(f"Dropdown {index + 1}")

                else:
                    print(f"[ℹ️] Skipping dropdown {index + 1} (only or two option)")

            except Exception as e:
                print(f"[❌] Error processing dropdown {index + 1}: {str(e)}")
                error_dropdowns.append(f"Dropdown {index + 1} - {str(e)}")
        return unchanged_dropdowns, error_dropdowns

    def scroll_element_by_selector(self, selector, pause_time=2, max_attempts=10):
        self.switch_to_dashboard_iframe()
        time.sleep(5)  # Allow iframe content to load

        script = f"""
            const el = document.querySelector('{selector}');
            if (!el) return [-1, -1, -1, false];
            el.scrollTop = el.scrollHeight;  // attempt to scroll
            const scrollTop = el.scrollTop;
            const clientHeight = el.clientHeight;
            const scrollHeight = el.scrollHeight;
            const isBottom = (scrollTop + clientHeight) >= scrollHeight;
            return [scrollTop, clientHeight, scrollHeight, isBottom];
        """

        for attempt in range(max_attempts):
            scrollTop, clientHeight, scrollHeight, isBottom = self.driver.execute_script(script)
            print(
                f"[Attempt {attempt + 1}] scrollTop: {scrollTop}, clientHeight: {clientHeight}, scrollHeight: {scrollHeight}, atBottom: {isBottom}")
            if isBottom:
                print("✅ Confirmed at bottom.")
                break
            time.sleep(pause_time)

    def find_vertical_scrollable_elements(self,selector=".ly-lineWrapper"):
        self.scroll_to_bottom_of_container(selector)
        time.sleep(7)
        iframe = self.driver.find_element(*self.IFRAME_LOCATOR)
        iframe_url=iframe.get_attribute("src")
        time.sleep(10)
        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[1])  # Switch to new tab
        # Step 3: Open iframe src URL directly
        time.sleep(2)
        self.driver.get(iframe_url)
        # WebDriverWait(self.driver, 10).until(
        #     lambda d: d.execute_script(f"return document.querySelector('{selector}') !== null")
        # )
        # scroll_script = f"""
        #     const el = document.querySelector('{selector}');
        #     if (!el) return [-1, -1, -1, false];
        #     el.scrollTop = el.scrollHeight;
        #     const scrollTop = el.scrollTop;
        #     const clientHeight = el.clientHeight;
        #     const scrollHeight = el.scrollHeight;
        #     const isBottom = (scrollTop + clientHeight) >= scrollHeight - 2;
        #     return [scrollTop, clientHeight, scrollHeight, isBottom];
        # """
        #
        # for attempt in range(max_attempts):
        #     scrollTop, clientHeight, scrollHeight, isBottom = self.driver.execute_script(scroll_script)
        #     print(
        #         f"[Attempt {attempt + 1}] scrollTop: {scrollTop}, clientHeight: {clientHeight}, scrollHeight: {scrollHeight}, atBottom: {isBottom}")
        #     if isBottom:
        #         print("✅ Reached bottom of .ly-lineWrapper.")
        #         return True
        #     time.sleep(pause_time)
        #
        # print("⚠️ Could not confirm scroll to bottom.")
        # return False















    
















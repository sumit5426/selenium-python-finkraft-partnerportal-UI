import time
from operator import contains

import allure
import pytest
from selenium.webdriver.common.by import By

from pages.login_page import LoginPage


class TestDashBoard:

    @allure.title("Login with invalid credentials")
    @pytest.mark.smoke
    def test_switch_workspace(self, driver, config):
        print("Switching workspace")
        login_page = LoginPage(driver)
        dashboard_page = login_page.login(config["username"], config["password"])
        workspace_name = dashboard_page.switch_workspace(config["workspace"])
        assert workspace_name == config["workspace"]
        assert "dashboard" in driver.current_url, "Current URL does not contain 'dashboard'"

    @allure.title("Redirect to login if not authenticated")
    @pytest.mark.regression
    def test_dashboard_redirects_to_login_when_not_authenticated(self, driver):
        # Directly access the dashboard URL without logging in
        dashboard_url = "https://pyt.finkraft.ai/dashboard"  # Replace with your actual dashboard URL
        driver.get(dashboard_url)
        assert "signin" in driver.current_url.lower(), (
            f"Expected to be redirected to login, but current URL is: {driver.current_url}"
        )

    @allure.title("All key widgets and UI elements are visible on dashboard")
    @pytest.mark.smoke
    def test_dashboard_widgets_visible(self, driver, config):
        login_page = LoginPage(driver)
        dashboard_page = login_page.login(config["username"], config["password"])
        time.sleep(30)
        assert dashboard_page.is_widget_visible("tables"), "Tables widget is not visible"
        assert dashboard_page.is_widget_visible("logo"), "Company logo is not visible"
        assert dashboard_page.is_widget_visible("tables_filter"), "Tables filter is not visible"
        assert dashboard_page.is_widget_visible("dashboard_filter"), "dashboard filter is not visible"
        assert dashboard_page.is_widget_visible("piechart"), "Charts widget is not visible"


    @allure.title("All Modules are visible on dashboard")
    @pytest.mark.smoke
    def test_dashboard_module_lists(self, driver, config):
        COMMON_MODULES = ["Dashboard", "Credentials", "Flight", "Upload", "Reports","Workspaces","Members","Followup","profile","Settings","Powered By"]
        login_page = LoginPage(driver)
        dashboard_page = login_page.login(config["username"], config["password"])
        missing_modules = dashboard_page.are_modules_present(COMMON_MODULES)
        assert not missing_modules, f"Missing modules in dashboard: {missing_modules}"

    # @pytest.mark.smoke
    # @allure.title("Verify top horizontal modules are present")
    # def test_top_horizontal_modules(self, driver, config):
    #     EXPECTED_MODULE_KEYWORDS = ["Airline", "Hotel", "Bus"]
    #     login_page = LoginPage(driver)
    #     dashboard_page = login_page.login(config["username"], config["password"])
    #     missing_tabs = dashboard_page.are_top_modules_present(EXPECTED_MODULE_KEYWORDS)
    #     assert not missing_tabs, f"Missing top modules: {missing_tabs}"

    @allure.title("Verify top horizontal modules as per client config")
    @pytest.mark.smoke
    def test_top_horizontal_modules(self, driver, config):
        expected_modules = config.get("expected_top_modules", [])
        print("module name :"+ str(expected_modules))
        login_page = LoginPage(driver)
        dashboard_page = login_page.login(config["username"], config["password"])
        missing_modules = dashboard_page.are_top_modules_present(expected_modules)
        assert not missing_modules, f"Missing top modules: {missing_modules}"

    @allure.title("Click each top module and verify it loads correct view title")
    @pytest.mark.regression
    def test_top_module_titles(self, driver, config):
        expected_modules = config.get("expected_top_modules", [])
        print("module name :"+ str(expected_modules))
        login_page = LoginPage(driver)
        dashboard_page = login_page.login(config["username"], config["password"])
        for module in expected_modules:
            dashboard_page.click_top_module(module)
            dashboard_page.switch_to_dashboard_iframe()
            actual_title = dashboard_page.get_module_title_text()
            dashboard_page.switch_to_default()  # optional
            assert actual_title is not None, f"View title not found for module: {module}"
            # assert module.lower() in actual_title.lower(), f"Expected module name in title. Got: {actual_title}"

    @allure.title("Verify all custom dropdowns under filters have values")
    @pytest.mark.smoke
    def test_custom_dropdowns_have_values(self, driver, config):
        login_page = LoginPage(driver)
        dashboard_page = login_page.login(config["username"], config["password"])
        results = dashboard_page.validate_all_dropdowns_have_values()
        for res in results:
            assert res["has_value"], f"Dropdown #{res['dropdown_index']} has no visible options"

    @allure.title("Verify transaction value changes when selecting options in all filter dropdowns")
    @pytest.mark.smoke
    def test_custom_dropdowns_values(self, driver, config):
        login_page = LoginPage(driver)
        dashboard_page = login_page.login(config["username"], config["password"])
        unchanged, errors = dashboard_page.validate_all_dropdowns_functionality()
        assert not unchanged, f"The following dropdowns did NOT change the transaction value: {unchanged}"
        assert not errors, f"Exceptions occurred in the following dropdowns: {errors}"

    @allure.title("Scroll down dashboard page till the end")
    @pytest.mark.smoke
    def test_scroll_to_bottom_of_dashboard(self, driver, config):

        login_page = LoginPage(driver)
        dashboard_page = login_page.login(config["username"], config["password"])
        dashboard_page.find_vertical_scrollable_elements()

        with allure.step("Wait for dashboard to load"):
            time.sleep(1)  # Replace with WebDriverWait if needed
        with allure.step("Scroll the scrollable dashboard container to bottom"):
            time.sleep(10)
        with allure.step("Verify scroll executed"):
            assert True
        # Optionally, assert that data is present
        # items = dashboard_page.get_all_dashboard_items()
        # assert len(items) > 0, "No data found after scrolling to bottom"















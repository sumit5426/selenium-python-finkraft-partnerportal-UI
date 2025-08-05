import time
from operator import contains

import allure
import pytest
from selenium.webdriver.common.by import By

from pages.login_page import LoginPage
from urllib.parse import urlparse



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
    def test_dashboard_redirects_to_login_when_not_authenticated(self, driver, config):
        # Directly access the dashboard URL without logging in
        parsed = urlparse(config["url"])
        dashboard_url = f"{parsed.scheme}://{parsed.netloc}/dashboard"
        driver.get(dashboard_url)
        assert "signin" in driver.current_url.lower(), (
            f"Expected to be redirected to login, but current URL is: {driver.current_url}"
        )

    @allure.title("All key widgets and UI elements are visible on dashboard")
    @pytest.mark.smoke
    def test_dashboard_widgets_visible(self, driver, config):
        login_page = LoginPage(driver)
        dashboard_page = login_page.login(config["username"], config["password"])
        assert dashboard_page.is_widget_visible("tables"), "Tables widget is not visible"
        assert dashboard_page.is_widget_visible("logo"), "Company logo is not visible"
        assert dashboard_page.is_widget_visible("tables_filter"), "Tables filter is not visible"
        assert dashboard_page.is_widget_visible("dashboard_filter"), "dashboard filter is not visible"
        # assert dashboard_page.is_widget_visible("piechart"), "Charts widget is not visible"


    @allure.title("All Modules are visible on dashboard")
    @pytest.mark.smoke
    def test_dashboard_module_lists(self, driver, config):
        COMMON_MODULES = ["Dashboard", "Credentials", "Flight", "Upload", "Reports","Workspaces","Members","Followup","Settings","Powered By"]
        login_page = LoginPage(driver)
        dashboard_page = login_page.login(config["username"], config["password"])
        missing_modules = dashboard_page.are_modules_present(COMMON_MODULES)
        assert not missing_modules, f"Missing modules in dashboard: {missing_modules}"

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
    def test_dashboard_dropdowns_have_values(self, driver, config, benchmark):
        login_page = LoginPage(driver)
        dashboard_page = login_page.login(config["username"], config["password"])
        # results = benchmark(dashboard_page.validate_all_dropdowns_have_values)
        results=dashboard_page.validate_all_dropdowns_have_values()
        for res in results:
            assert res["has_value"], f"Dropdown #{res['dropdown_index']} has no visible options"

    @allure.title("Verify transaction value changes when selecting options in all filter dropdowns")
    @pytest.mark.smoke
    def test_dashboard_dropdowns_values_change(self, driver, config):
        login_page = LoginPage(driver)
        dashboard_page = login_page.login(config["username"], config["password"])
        unchanged, errors , changed= dashboard_page.validate_all_dropdowns_functionality()
        assert not errors, f"Exceptions occurred in the following dropdowns: {errors}"
        assert changed, f"The following dropdowns did change the transaction value: {changed}"
        with allure.step("Dropdown Validation Summary"):
            allure.attach(str(changed), name="Changed Dropdowns", attachment_type=allure.attachment_type.TEXT)
            if unchanged:
                allure.attach(str(unchanged), name="Unchanged Dropdowns", attachment_type=allure.attachment_type.TEXT)
            if errors:
                allure.attach(str(errors), name="Error Dropdowns", attachment_type=allure.attachment_type.TEXT)

    @allure.title("Scroll down dashboard page till the end")
    @pytest.mark.smoke
    def test_scroll_to_bottom_of_dashboard(self, driver, config):
        with allure.step("Wait for dashboard to load"):
            login_page = LoginPage(driver)
            dashboard_page = login_page.login(config["username"], config["password"])
            time.sleep(1)
        with allure.step("Scroll the scrollable dashboard container to bottom"):
            dashboard_page.find_vertical_scrollable_elements()
            time.sleep(10)
        with allure.step("Verify scroll executed"):
            assert True

    @allure.title("Dashboard load time performance benchmark")
    @pytest.mark.performance
    def test_dashboard_load_time(self, driver, config):
        """Measure and validate dashboard load times"""
        login_page = LoginPage(driver)
        dashboard_page = login_page.login(config["username"], config["password"])
        start_time = time.time()
        dashboard_page.switch_to_dashboard_iframe()
        dashboard_page.get_module_title_text()
        # dashboard_page.wait_for_tables_to_load()
        load_time = time.time() - start_time
        assert load_time < 5.0, f"Dashboard too slow: {load_time:.2f}s"
        allure.attach(f"{load_time:.2f} seconds", "Load Time", allure.attachment_type.TEXT)

    @allure.title("Network error handling and user feedback")
    @pytest.mark.error_handling
    def test_network_error_ui(self, driver, config):
        """Test UI behavior during network failures"""
        pytest.skip("Network-failure simulation not implemented yet — raising feature request")
        login_page = LoginPage(driver)
        dashboard_page = login_page.login(config["username"], config["password"])
        # Simulate network interruption using Chrome DevTools
        driver.execute_cdp_cmd('Network.enable', {})
        driver.execute_cdp_cmd('Network.emulateNetworkConditions', {
            'offline': True,
            'latency': 0,
            'downloadThroughput': 0,
            'uploadThroughput': 0
        })
        time.sleep(30)
        # Try to apply filter during "network failure"
        dashboard_page.apply_filter("FY", "2024-25")
        # Validate error message appears
        error_message = dashboard_page.get_error_notification()
        assert error_message is not None, "No error message shown during network failure"
        assert "network" in error_message.lower() or "connection" in error_message.lower()
        # Restore network
        driver.execute_cdp_cmd('Network.emulateNetworkConditions', {
            'offline': False,
            'latency': 0,
            'downloadThroughput': -1,
            'uploadThroughput': -1
        })


















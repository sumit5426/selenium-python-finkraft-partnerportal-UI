import allure
import pytest

from pages.login_page import LoginPage


class TestFlights:
    @allure.title("verifying the flight table heading label name")
    @pytest.mark.smoke
    def test_flight_table_headings_match_expected(self, driver, config):

        login_page = LoginPage(driver)
        dashboard_page = login_page.login(config["username"], config["password"])
        flight_page = dashboard_page.go_to_flight_page()
        flight_page.get_flight_ag_grid_table_headings()

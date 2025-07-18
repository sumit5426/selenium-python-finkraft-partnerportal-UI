import allure
import pytest
from pages.login_page import LoginPage


class TestCredentials:
    @allure.title("verifying take action button functionality")
    @pytest.mark.smoke
    def test_take_action_button_functionality(self, driver, config):
        login_page = LoginPage(driver)
        dashboard_page=login_page.login(config["username"], config["password"])
        credentials_page=dashboard_page.go_to_credentials()
        credentials_page.click_take_action_button()

    @allure.title("verifying the no of the cards")
    @pytest.mark.smoke
    def test_three_integration_cards_present(self,driver, config):
        login_page = LoginPage(driver)
        dashboard_page = login_page.login(config["username"], config["password"])
        credentials_page = dashboard_page.go_to_credentials()
        cards = credentials_page.get_integration_cards()
        assert len(cards) == 3, f"Expected 3 integration cards, found {len(cards)}"

    @allure.title("verifying the label name the cards")
    @pytest.mark.smoke
    def test_card_labels_are_correct(self,driver, config):
        expected_labels = ["GST Credential", "Airline Credential", "SSR Credential"]
        dashboard_page = login_page.login(config["username"], config["password"])
        credentials_page = dashboard_page.go_to_credentials()
        labels = credentials_page.get_card_labels()
        assert labels == expected_labels, f"Expected labels {expected_labels}, but got {labels}"

    @allure.title("verifying the GST table heading label name")
    @pytest.mark.smoke
    def test_gst_table_headings_match_expected(self,driver, config):
        expected_headings = ['Group', 'GSTIN', 'Username', 'Password', 'Status', 'Last Edited']
        login_page = LoginPage(driver)
        dashboard_page = login_page.login(config["username"], config["password"])
        credentials_page = dashboard_page.go_to_credentials()
        actual_headings = credentials_page.get_gst_ag_grid_table_headings()
        assert actual_headings == expected_headings, (
            f"Expected AG Grid headings {expected_headings}, but got {actual_headings}"
        )

    @allure.title("verifying the airline table heading label name")
    @pytest.mark.smoke
    def test_airline_table_headings_match_expected(self, driver, config):
        expected_headings = ['Group', 'Airlines', 'PAN', 'Username', 'Password', 'App Code', 'OTP Email']
        login_page = LoginPage(driver)
        dashboard_page = login_page.login(config["username"], config["password"])
        credentials_page = dashboard_page.go_to_credentials()
        actual_headings = credentials_page.get_airline_ag_grid_table_headings()
        assert actual_headings == expected_headings, (
            f"Expected AG Grid headings {expected_headings}, but got {actual_headings}"
        )








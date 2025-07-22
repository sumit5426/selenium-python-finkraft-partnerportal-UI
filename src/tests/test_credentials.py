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
        login_page = LoginPage(driver)
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
        if not actual_headings:
            pytest.skip("No data present, so table headings are not rendered.")
        assert actual_headings == expected_headings, (
            f"Expected AG Grid headings {expected_headings}, but got {actual_headings}"
        )
        actual_headings_in_no_action_tab = credentials_page.click_no_action_required_gst_tab()
        if not actual_headings:
            pytest.skip("No data present, so no action table headings are not rendered.")
        assert actual_headings_in_no_action_tab == expected_headings, (
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
        if not actual_headings:
            pytest.skip("No data present, so table headings are not rendered.")
        assert actual_headings == expected_headings, (
            f"Expected AG Grid headings {expected_headings}, but got {actual_headings}"
        )
        actual_headings_in_no_action_tab = credentials_page.click_no_action_required_airline_tab()
        if not actual_headings_in_no_action_tab:
            pytest.skip("No data present, so no action table headings are not rendered.")
        assert actual_headings_in_no_action_tab == expected_headings, (
            f"Expected AG Grid headings in no action tab {expected_headings}, but got {actual_headings}"
        )

    @allure.title("verifying the email table heading label name")
    @pytest.mark.smoke
    def test_email_table_headings_match_expected(self, driver, config):
        expected_headings = ['Worksapce', 'Email', 'Password', 'App Code', 'Status','Action']
        login_page = LoginPage(driver)
        dashboard_page = login_page.login(config["username"], config["password"])
        credentials_page = dashboard_page.go_to_credentials()
        actual_headings = credentials_page.get_email_ag_grid_table_headings()
        if not actual_headings:
            pytest.skip("No data present, so table headings are not rendered.")
        assert actual_headings == expected_headings, (
            f"Expected AG Grid headings {expected_headings}, but got {actual_headings}"
        )
        actual_headings_in_no_action_tab = credentials_page.click_no_action_required_email_tab()
        if not actual_headings_in_no_action_tab:
            pytest.skip("No data present, so no action table headings are not rendered.")
        assert actual_headings_in_no_action_tab == expected_headings, (
            f"Expected AG Grid headings in no action tab {expected_headings}, but got {actual_headings}"
        )


    @pytest.mark.parametrize("module", ["gst", "airline", "email"])
    @pytest.mark.smoke
    def test_toggle_buttons_expand_and_collapse(self, driver, config, module):
        login_page = LoginPage(driver)
        dashboard_page = login_page.login(config["username"], config["password"])
        credentials_page = dashboard_page.go_to_credentials()
        credentials_page.select_module(module)
        if not credentials_page.has_table_headings():
            pytest.skip(f"No table headings for module '{module}', so no toggle buttons to test.")
        count = credentials_page.get_toggle_button_count()
        if count == 0:
            pytest.skip(f"No toggle buttons present for module '{module}'.")
        for idx in range(count):
            # Expand
            state = credentials_page.click_toggle_button_and_wait(index=idx, expected_state="true")
            assert state == "true", f"Button {idx} in module '{module}' did not expand"
            # Collapse
            state = credentials_page.click_toggle_button_and_wait(index=idx, expected_state="false")
            assert state == "false", f"Button {idx} in module '{module}' did not collapse"

    @pytest.mark.parametrize("module", ["gst", "airline", "email"])
    @pytest.mark.smoke
    def test_column_toggle_checkbox_reflects_in_table_headings(self,driver, config, module):
        login_page = LoginPage(driver)
        dashboard_page = login_page.login(config["username"], config["password"])
        credentials_page = dashboard_page.go_to_credentials()
        # 1. Open the column selector
        credentials_page.select_module(module)
        if not credentials_page.has_table_headings():
            pytest.skip(f"No table headings for module '{module}', so no toggle buttons to test.")
        credentials_page.open_column_selector(toggle_index=0)  # column toggle index
        checkboxes = credentials_page.get_column_checkboxes()
        labels = credentials_page.get_checkbox_labels()
        assert len(checkboxes) == len(labels), "Checkboxes and labels count mismatch"
        for idx, (checkbox, label_text) in enumerate(zip(checkboxes, labels)):
            # Determine current state
            aria_label = checkbox.get_attribute("aria-label")
            is_selected = "visible" in aria_label
            credentials_page.toggle_checkbox_and_wait(checkbox, expected_visible=not is_selected)
            # If now visible, the column should appear in table headings
            if not is_selected:
                table_headings = credentials_page.get_table_headings()
                assert label_text in table_headings, (
                    f"After selecting, label '{label_text}' not found in table headings {table_headings}"
                )
            else:
                # If now hidden, the column / column name should NOT appear in table headings
                table_headings = credentials_page.get_table_headings()
                assert label_text not in table_headings, (
                    f"After deselecting, label '{label_text}' should not be in table headings {table_headings}"
                )
            credentials_page.toggle_checkbox_and_wait(checkbox, expected_visible=is_selected)
















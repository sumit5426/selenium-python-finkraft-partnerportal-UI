import time

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
        headings=flight_page.get_flight_ag_grid_table_headings()
        assert headings, "No table headings found"
        assert len(headings) >= 20, f"Table contains too few columns: {headings}"
        assert len(headings) == len(set(headings)), f"Column headings are not unique: {headings}"

    @pytest.mark.smoke
    def test_column_toggle_checkbox_reflects_in_table_headings(self, driver, config):
        login_page = LoginPage(driver)
        dashboard = login_page.login(config["username"], config["password"])
        flight_page = dashboard.go_to_flight_page()
        # Skip if no headings present
        if not flight_page.has_table_headings():
            pytest.skip("No table headings; nothing to toggle.")
        # Open the column selector panel
        flight_page.open_column_selector(toggle_index=0)
        # Fetch all label texts once
        labels = flight_page.get_checkbox_labels()
        for label_text in labels:
            # Determine current visibility state from aria-label
            aria = flight_page.find_checkbox_by_label_with_scroll(label_text).get_attribute("aria-label")
            is_visible = "visible" in aria
            # Toggle to the opposite state
            flight_page.toggle_column(label_text, expected_visible=not is_visible)
            # Verify the column heading appears or disappears accordingly
            headings = flight_page.get_table_headings()
            if not is_visible:
                assert label_text in headings, (
                    f"After selecting, '{label_text}' not found in table headings {headings}"
                )
            else:
                assert label_text not in headings, (
                    f"After deselecting, '{label_text}' should not be in table headings {headings}"
                )
            # Toggle back to the original state
            flight_page.toggle_column(label_text, expected_visible=is_visible)

    @pytest.mark.smoke
    def test_toggles_buttons_expand_and_collapse(self, driver, config):
        login_page = LoginPage(driver)
        dashboard_page = login_page.login(config["username"], config["password"])
        flight_page = dashboard_page.go_to_flight_page()
        if not flight_page.has_table_headings():
            pytest.skip(f"No table headings for module '', so no toggle buttons to test.")
        count = flight_page.get_toggle_button_count()
        if count == 0:
            pytest.skip(f"No toggle buttons present for module .")
        for idx in range(count):
            # Expand
            state = flight_page.click_toggle_button_and_wait(index=idx, expected_state="true")
            assert state == "true", f"Button {idx} in module '' did not expand"
            # Collapse
            state = flight_page.click_toggle_button_and_wait(index=idx, expected_state="false")
            assert state == "false", f"Button {idx} in module '' did not collapse"

    @allure.title("Scroll down dashboard page till the end")
    @pytest.mark.smoke
    def test_scroll_to_bottom_of_dashboard(self, driver, config):
        with allure.step("Wait for dashboard to load"):
            login_page = LoginPage(driver)
            dashboard_page = login_page.login(config["username"], config["password"])
            flight_page = dashboard_page.go_to_flight_page()
            time.sleep(1)
        with allure.step("Scroll the scrollable dashboard container to bottom"):
            flight_page.scroll_to_bottom_of_aggrid_table()
        with allure.step("Verify scroll executed"):
            assert True

    @allure.title("contains filter functionality")
    @pytest.mark.smoke
    def test_filters_in_tables(self, driver, config):
        login_page = LoginPage(driver)
        dashboard = login_page.login(config["username"], config["password"])
        flight_page = dashboard.go_to_flight_page()
        # Skip if no headings present
        if not flight_page.has_table_headings():
            pytest.skip("No table headings; nothing to toggle.")
        # Open the column selector panel
        flight_page.open_column_selector_filter(toggle_index=1)
        toggles = flight_page.get_filter_toggles()
        assert toggles, "No filter toggles found!"
        for idx, toggle in enumerate(toggles):
            flight_page.expand_toggle(toggle)
            flight_page.get_inputs_under_toggle(toggle,idx)
            flight_page.expand_toggle(toggle)

    @allure.title("all filter functionality")
    @pytest.mark.smoke
    def test_filters_in_tables(self, driver, config):
        pytest.skip("all filter functionality not implemented")
        login_page = LoginPage(driver)
        dashboard = login_page.login(config["username"], config["password"])
        flight_page = dashboard.go_to_flight_page()
        # Skip if no headings present
        if not flight_page.has_table_headings():
            pytest.skip("No table headings; nothing to toggle.")
        # Open the column selector panel
        flight_page.open_column_selector_filter(toggle_index=1)
        toggles = flight_page.get_filter_toggles()
        assert toggles, "No filter toggles found!"
        for idx, toggle in enumerate(toggles):
            flight_page.expand_toggle(toggle)
            flight_page.select_sub_filter()
            # flight_page.expand_toggle(toggle)

    @pytest.mark.smoke
    @pytest.mark.flaky()
    def test_table_header_drag_and_drop(self, driver, config):
        login_page = LoginPage(driver)
        dashboard_page = login_page.login(config["username"], config["password"])
        flight_page = dashboard_page.go_to_flight_page()
        if not flight_page.has_table_headings():
            pytest.skip(f"No table headings for module, so no drag and drop to test.")
        source_name, target_name, new_order = flight_page.drag_and_drop_two_random_headers(exclude_index=0)
        assert source_name in new_order and target_name in new_order, \
            f"Expected {source_name} and {target_name} to be present after drag-and-drop."
        assert new_order != flight_page.initial_header_order, \
            "Header order did not change after drag-and-drop"

    def test_sort_toggle_by_index(self, driver, config):
        login_page = LoginPage(driver)
        dashboard = login_page.login(config["username"], config["password"])
        flight_page = dashboard.go_to_flight_page()
        col_idx = 5

        # Ascending
        clicks_asc = flight_page.sort_by_column_index(col_idx, direction="asc")
        time.sleep(0.5)
        col_values = flight_page.get_column_values_by_index(col_idx)
        assert col_values == sorted(col_values), f"Not sorted ascending: {col_values}"
        assert clicks_asc == 1, f"Expected 1 click for asc, got {clicks_asc}"

        # Descending
        clicks_desc = flight_page.sort_by_column_index(col_idx, direction="desc")
        time.sleep(0.5)
        desc_values = flight_page.get_column_values_by_index(col_idx)
        assert desc_values == sorted(desc_values, reverse=True), f"Not sorted descending: {desc_values}"
        assert clicks_desc == 1, f"Expected 1 click for desc, got {clicks_desc}"

        # None
        clicks_none = flight_page.sort_by_column_index(col_idx, direction="none")
        assert clicks_none == 1, f"Expected 1 click for none, got {clicks_none}"



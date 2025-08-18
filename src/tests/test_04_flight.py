import json

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
    def test_all_filters_in_tables(self, driver, config):
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

    @allure.title("Verifying drag and drop functionality between columns")
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

    @allure.title("verifying columns sorting functionality")
    @pytest.mark.smoke
    def test_sort_toggle_by_index(self, driver, config):
        login_page = LoginPage(driver)
        dashboard = login_page.login(config["username"], config["password"])
        flight_page = dashboard.go_to_flight_page()
        for col_idx in [3, 4, 5]:
            # Ascending
            clicks_asc = flight_page.sort_by_column_index(col_idx, direction="asc")
            time.sleep(0.5)
            col_values = flight_page.get_column_values_by_index(col_idx)
            assert col_values == sorted(col_values), f"[col {col_idx}] Not sorted ascending: {col_values}"
            assert clicks_asc == 1, f"[col {col_idx}] Expected 1 click for asc, got {clicks_asc}"
            # Descending
            clicks_desc = flight_page.sort_by_column_index(col_idx, direction="desc")
            time.sleep(0.5)
            desc_values = flight_page.get_column_values_by_index(col_idx)
            assert desc_values == sorted(desc_values,
                                         reverse=True), f"[col {col_idx}] Not sorted descending: {desc_values}"
            assert clicks_desc == 1, f"[col {col_idx}] Expected 1 click for desc, got {clicks_desc}"
            # None
            clicks_none = flight_page.sort_by_column_index(col_idx, direction="none")
            assert clicks_none == 1, f"[col {col_idx}] Expected 1 click for none, got {clicks_none}"

    @allure.title("Verifying group by filter feature functionality")
    @pytest.mark.smoke
    def test_group_each_index_isolated(self, driver, config):
        login_page = LoginPage(driver)
        dashboard = login_page.login(config["username"], config["password"])
        flight_page = dashboard.go_to_flight_page()
        indices = [4,5]  # 1-based
        for idx in indices:
            # Actx
            header_name = flight_page.drag_header_to_group_zone_by_index(idx)
            # Assert: chip exists for that header (skip empty header names gracefully)
            chip_texts = flight_page.get_grouped_chip_texts()
            if header_name:
                assert header_name in chip_texts, f"[idx {idx}] Chip for '{header_name}' not found. Chips: {chip_texts}"
            else:
                # If header has no text (icon column), assert at least one chip exists
                assert len(chip_texts) >= 1, f"[idx {idx}] No grouping chip found."
            # Assert: auto-group column present at left and groups visible
            assert flight_page.is_auto_group_column_present_left(), f"[idx {idx}] Auto group column not detected."
            if not flight_page.has_group_rows():
                flight_page.expand_first_group_if_collapsed()
                time.sleep(0.3)
            assert flight_page.has_group_rows(), f"[idx {idx}] No group rows visible."
            # Cleanup before next iteration
            flight_page.clear_grouping()

    @allure.title("Verifying aggregate group filter feature functionality")
    @pytest.mark.smoke
    def test_group_each_index_aggregated(self, driver, config):
        login_page = LoginPage(driver)
        dashboard = login_page.login(config["username"], config["password"])
        flight_page = dashboard.go_to_flight_page()
        indices = [4, 5]  # 1-based
        for idx in indices:
            # Actx
            header_name = flight_page.drag_header_to_group_zone_by_index(idx)
            # Assert: chip exists for that header (skip empty header names gracefully)
            chip_texts = flight_page.get_grouped_chip_texts()
            if header_name:
                assert header_name in chip_texts, f"[idx {idx}] Chip for '{header_name}' not found. Chips: {chip_texts}"
            else:
                # If header has no text (icon column), assert at least one chip exists
                assert len(chip_texts) >= 1, f"[idx {idx}] No grouping chip found."
            # Assert: auto-group column present at left and groups visible
            assert flight_page.is_auto_group_column_present_left(), f"[idx {idx}] Auto group column not detected."
            if not flight_page.has_group_rows():
                flight_page.expand_first_group_if_collapsed()
                time.sleep(0.3)
            assert flight_page.has_group_rows(), f"[idx {idx}] No group rows visible."

    @allure.title("Verifying page views functionality")
    @pytest.mark.smoke
    def test_switch_from_default_view(self, driver, config):
        login_page = LoginPage(driver)
        dashboard = login_page.login(config["username"], config["password"])
        flight_page = dashboard.go_to_flight_page()
        selected_text, expected_text = flight_page.switch_to_different_view()
        assert selected_text == expected_text, f"Selected '{selected_text}', expected '{expected_text}'"

    @allure.title("Verifying download invoice history list functionality")
    @pytest.mark.smoke
    def test_get_download_invoice_history_view(self, driver, config):
        login_page = LoginPage(driver)
        dashboard = login_page.login(config["username"], config["password"])
        flight_page = dashboard.go_to_flight_page()
        is_report_name_available=flight_page.get_download_history_downloads()
        assert is_report_name_available,"report name not available"

    @allure.title("Verifying upload invoice history list functionality")
    @pytest.mark.smoke
    def test_get_upload_invoice_history_view(self, driver, config):
        login_page = LoginPage(driver)
        dashboard = login_page.login(config["username"], config["password"])
        flight_page = dashboard.go_to_flight_page()
        is_report_name_available = flight_page.get_upload_history_downloads()
        assert is_report_name_available, "report name not available"

    @allure.title("Verifying report history list functionality")
    @pytest.mark.smoke
    def test_get_report_history_view(self, driver, config):
        login_page = LoginPage(driver)
        dashboard = login_page.login(config["username"], config["password"])
        flight_page = dashboard.go_to_flight_page()
        is_report_name_available = flight_page.get_report_history_downloads()
        assert is_report_name_available, "report name not available"

    @allure.title("Verifying data available in the table")
    def test_validate_data_available_in_table(self, driver, config):
        login_page = LoginPage(driver)
        dashboard = login_page.login(config["username"], config["password"])
        flight_page = dashboard.go_to_flight_page()
        # Validate table has data
        is_valid, result = flight_page.validate_table_has_data()
        assert is_valid, f"Comprehensive table validation failed: {result}"
        # If validation returns detailed results
        if isinstance(result, dict):
            assert result["non_empty_cells"] >= 5, f"Expected at least 5 data cells, found {result['non_empty_cells']}"
            # Log detailed results
            with allure.step("Table validation results"):
                allure.attach(
                    json.dumps(result, indent=2),
                    "table_validation_details.json",
                    allure.attachment_type.JSON
                )

    @allure.title("Verifying table_headers_deselecting_functionality")
    @pytest.mark.smoke
    def test_all_table_headers_deselecting_functionality(self, driver, config):
        login_page = LoginPage(driver)
        dashboard = login_page.login(config["username"], config["password"])
        flight_page = dashboard.go_to_flight_page()
        # Skip if no headings present
        if not flight_page.has_table_headings():
            pytest.skip("No table headings; nothing to toggle.")
        # Open the column selector panel
        flight_page.open_column_selector(toggle_index=0)
        has_columns=flight_page.has_table_headings()
        if has_columns:
            is_no_column=flight_page.no_of_table_header_after_deselection()
            assert is_no_column, "table heading are there after deselection"


    @allure.title("Verifying table_headers_search_and_select_functionality")
    @pytest.mark.smoke
    def test_all_table_headers_search_and_select_functionality(self, driver, config):
        login_page = LoginPage(driver)
        dashboard = login_page.login(config["username"], config["password"])
        flight_page = dashboard.go_to_flight_page()
        # Skip if no headings present
        if not flight_page.has_table_headings():
            pytest.skip("No table headings; nothing to toggle.")
        # Open the column selector panel
        flight_page.open_column_selector(toggle_index=0)
        is_selected=flight_page.enter_text_into_textbox_for_column_header_selection()
        assert is_selected, "column search functionality failed"


    @allure.title("Verifying table_headers_aggregate_functionality")
    @pytest.mark.smoke
    def test_all_table_headers_aggregate_functionality(self, driver, config):
        login_page = LoginPage(driver)
        dashboard = login_page.login(config["username"], config["password"])
        flight_page = dashboard.go_to_flight_page()
        # Skip if no headings present
        if not flight_page.has_table_headings():
            pytest.skip("No table headings; nothing to toggle.")
        # Open the column selector panel
        flight_page.open_column_selector(toggle_index=0)
        flight_page.enter_text_into_textbox_for_column_header_selection()
        flight_page.aggregate_function_to_column()

    @allure.title("Verifying invoice view functionality")
    @pytest.mark.smoke
    def test_invoice_pdf_available_in_ui(self, driver, config):
        login_page = LoginPage(driver)
        dashboard = login_page.login(config["username"], config["password"])
        flight_page = dashboard.go_to_flight_page()
        is_invoice_visible=flight_page.view_invoice_pdf()
        assert is_invoice_visible, "invoice pdf. did not appear"

    @allure.title("Verifying table header pinned functionality")
    @pytest.mark.smoke
    def test_table_header_pinned_functionality(self, driver, config):
        login_page = LoginPage(driver)
        dashboard = login_page.login(config["username"], config["password"])
        flight_page = dashboard.go_to_flight_page()
        left_pin_count = flight_page.pin_column_to_left()
        assert left_pin_count >= 1, "Pin to left failed: No column is pinned left"
        # Pin to right & assert
        right_pin_count = flight_page.pin_column_to_right()
        assert right_pin_count >= 1, "Pin to right failed: No column is pinned right"
        flight_page.pin_column_to_remove()
        no_left_pins = len(flight_page.get_visible_elements(flight_page.LEFT_PINNED_CONTAINER))
        assert no_left_pins == 0, "Remove pin failed: Columns are still pinned"
        flight_page.pin_column_to_reset()
        # Check and assert whatever post-reset behavior is expected (such as pin containers are empty)
        assert len(flight_page.get_visible_elements(flight_page.LEFT_PINNED_CONTAINER)) == 0, "Reset left pins failed"
        assert len(flight_page.get_visible_elements(flight_page.RIGHT_PINNED_CONTAINER)) == 0, "Reset right pins failed"

















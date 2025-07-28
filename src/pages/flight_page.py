from selenium.webdriver.common.by import By

from utils.browser_utility import BrowserUtility


class FlightPage(BrowserUtility):
    def __init__(self, driver):
        super().__init__(driver)

    AG_GRID_SCROLL_CONTAINER_LOCATOR=(By.CSS_SELECTOR,".ag-header-viewport")
    TABLE_HEADING_LABEL_LOCATOR=(By.XPATH,'//span[@ref="eText" and @class="ag-header-cell-text"]')




    def get_flight_ag_grid_table_headings(self):
        """Returns a list of AG Grid table heading texts."""
        headings = []
        seen = set()
        # Get the scrollable container (usually a div with overflow-x: auto)
        scroll_container = self.driver.find_element(*self.AG_GRID_SCROLL_CONTAINER_LOCATOR)  # Adjust selector as needed
        # Scroll to the far left
        self.driver.execute_script("arguments[0].scrollLeft = 0;", scroll_container)
        last_scroll = -1
        while True:
            # Collect visible headings
            elements = self.wait_for_all_elements(self.TABLE_HEADING_LABEL_LOCATOR)
            for el in elements:
                text = el.text.strip()
                if text and text not in seen:
                    headings.append(text)
                    seen.add(text)
            # Scroll right by a chunk
            current_scroll = self.driver.execute_script("return arguments[0].scrollLeft;", scroll_container)
            max_scroll = self.driver.execute_script("return arguments[0].scrollWidth - arguments[0].clientWidth;",
                                                    scroll_container)
            print(f"Scrolling... current: {current_scroll}, max: {max_scroll}")
            if current_scroll == max_scroll or current_scroll == last_scroll:
                print("headheadings:"+str(headings))
                break
            self.driver.execute_script("arguments[0].scrollLeft += 200;", scroll_container)
            last_scroll = current_scroll
        return list(headings)
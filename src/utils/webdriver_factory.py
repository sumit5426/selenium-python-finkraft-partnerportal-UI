import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions


class WebDriverFactory:

    @staticmethod
    def get_driver(browser="chrome", headless=False, execution="local"):
        driver = None

        if execution.lower() == "local":
            if browser.lower() == "chrome":
                options = ChromeOptions()
                options.add_argument("--start-maximized")
                options.add_argument("--disable-notifications")
                if headless:
                    options.add_argument("--headless=new")
                    options.add_argument("--window-size=1920,1080")
                driver = webdriver.Chrome(options=options)

            elif browser.lower() == "firefox":
                options = FirefoxOptions()
                if headless:
                    options.add_argument("--headless")
                    options.add_argument("--width=1920")
                    options.add_argument("--height=1080")
                driver = webdriver.Firefox(options=options)
                driver.maximize_window()

            elif browser.lower() == "edge":
                options = EdgeOptions()
                if headless:
                    options.add_argument("--headless")
                    options.add_argument("--window-size=1920,1080")
                driver = webdriver.Edge(options=options)
                driver.maximize_window()

            else:
                raise ValueError(f"Unsupported browser: {browser}")

        elif execution.lower() == "cloud":
            username = os.environ.get("BROWSERSTACK_USERNAME")
            access_key = os.environ.get("BROWSERSTACK_ACCESS_KEY")
            if not username or not access_key:
                raise Exception("BrowserStack credentials not set in environment variables.")

            # 📌 Define capabilities for BrowserStack directly
            desired_cap = {
                "browserName": "Chrome",
                "browserVersion": "latest",
                "bstack:options": {
                    "os": "Windows",
                    "osVersion": "10",
                    "resolution": "1920x1080",
                    "projectName": "Selenium PyTest Framework",
                    "buildName": "Build 1.0",
                    "sessionName": "Automated Test",
                    "local": "false",
                    "seleniumVersion": "4.10.0"
                }
            }

            remote_url = f"https://{username}:{access_key}@hub-cloud.browserstack.com/wd/hub"
            driver = webdriver.Remote(
                command_executor=remote_url,
                desired_capabilities=desired_cap
            )

        else:
            raise ValueError(f"Unsupported execution type: {execution}")

        driver.implicitly_wait(10)
        driver.set_page_load_timeout(30)
        driver.set_script_timeout(30)
        return driver
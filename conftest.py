import datetime

import pytest
import yaml
import os
from pathlib import Path
import allure

from src.utils.webdriver_factory import WebDriverFactory




def pytest_addoption(parser):
    # set value from command line or set default value
    parser.addoption("--env", action="store", default=None, help="Environment: QA, staging, prod")
    parser.addoption("--client", action="store", default=None, help="Client name")
    parser.addoption("--workspace", action="store", default=None, help="Workspace name")
    parser.addoption("--browser", action="store", default="chrome", help="Browser: chrome, firefox, edge")
    parser.addoption("--headless", action="store", default="false", help="Headless mode: true/false")
    parser.addoption("--execution", action="store", default="local", help="Execution: local/cloud")


@pytest.fixture(scope="session")
def config(request):
    config_path = Path(__file__).resolve().parent / "src" / "config" / "config.yaml"
    with open(config_path, "r") as f:
        # yaml to dict
        conf = yaml.safe_load(f)

    # retrieve value from command line and configuration file
    env = request.config.getoption("--env") or conf["default_env"]
    client = request.config.getoption("--client") or conf["default_client"]
    workspace = request.config.getoption("--workspace")
    headless = request.config.getoption("--headless").lower() in ("true", "1", "yes")
    browser = request.config.getoption("--browser")
    execution = request.config.getoption("--execution")

    # Retrieving userid, password and url of particular client
    client_data = conf["environments"][env]["clients"][client]

    if not workspace:
        workspaces = client_data.get("workspaces", [])
        if workspaces:
            workspace = workspaces[0]
        else:
            workspace = conf.get("default_workspace")
            if not workspace:
                raise Exception(f"No workspace defined for client: {client} in env: {env}")

    # return statement is used so that we can get access these details across framework
    return {
        "env": env,
        "client": client,
        "workspace": workspace,
        "url": client_data["url"],
        "username": client_data["username"],
        "password": client_data["password"],
        "browser": browser,
        "headless": headless,
        "execution": execution
    }


@pytest.fixture(scope="function")
def driver(config):
    driver = WebDriverFactory.get_driver(
        browser=config["browser"],
        headless=config["headless"],
        execution=config["execution"]
    )
    driver.get(config["url"])
    driver.maximize_window()
    # logger.info(f"Started browser for {config['client']} at {config['url']}")
    yield driver
    # logger.info(f"Finished browser for {config['client']} at {config['url']}")
    driver.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        driver = item.funcargs.get("driver")
        if driver:
            screenshot_dir = "reports/screenshots"
            os.makedirs(screenshot_dir, exist_ok=True)
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            file_name = f"{item.name}_{timestamp}.png"
            screenshot_path = os.path.join(screenshot_dir, file_name)
            driver.save_screenshot(screenshot_path)

            # Attach screenshot to Allure
            with open(screenshot_path, "rb") as image_file:
                allure.attach(
                    image_file.read(),
                    name=file_name,
                    attachment_type=allure.attachment_type.PNG
                )

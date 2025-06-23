import time

from pages.login_page import LoginPage


class TestDashBoard:

   def test_switch_workspace(self,driver,config):
       print("Switching workspace")
       login_page = LoginPage(driver)
       dashboard_page=login_page.login(config["username"], config["password"])
       workspace_name=dashboard_page.switch_workspace(config["workspace"])
       assert workspace_name==config["workspace"]
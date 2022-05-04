import yaml
from login_page import LoginPage
import time
from home_page import HomePage
from selenium.webdriver.common.by import By


ACCOUNT_EMAIL = ""
ACCOUNT_PASSWORD = ""


def main():
    pass


if __name__ == "__main__":
    from selenium import webdriver
    with open("config.yaml", "r") as stream:
        try:
            parameters = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise exc

    path = "/Users/tiendnguyen/Desktop/chromedriver"
    driver = webdriver.Chrome(executable_path=path)
    login_driver = LoginPage(driver, parameters=parameters)
    login_driver.open_url()
    home_driver = login_driver.login_valid_user()
    search_driver = home_driver.search_job()
    search_driver.apply_filter()
    time.sleep(5)
    search_driver.browsing_jobs()

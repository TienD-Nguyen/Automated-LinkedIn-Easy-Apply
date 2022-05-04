from page import BasePage
from home_page import HomePage
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from locators import Locators


class LoginPage(BasePage):
    def __init__(self, driver, parameters=None, url=None):
        super(LoginPage, self).__init__(driver, parameters)
        if url is None:
            self.url = "https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin"
        else:
            self.url = url
        self.username = parameters["email"]
        self.password = parameters["password"]

    def login_valid_user(self):
        # self.driver.find_element(*Locators.USERNAME_INPUT).send_keys(username)
        # self.driver.find_element(*Locators.PASSWORD_INPUT).send_keys(password)
        # self.driver.find_element(*Locators.LOGIN_BUTTON).click()
        try:
            self.enter_text(Locators.USERNAME_INPUT, self.username)
            self.enter_text(Locators.PASSWORD_INPUT, self.password)
            self.click(Locators.LOGIN_BUTTON)
            return HomePage(driver=self.driver, url=self.driver.current_url, parameters=self.parameters)
        except TimeoutError:
            raise Exception("TimeoutException! Username/password field or login button not found")

    def open_url(self):
        self.driver.get(self.url)
        return self


if __name__ == "__main__":
    from selenium import webdriver
    path = "/Users/tiendnguyen/Desktop/chromedriver"
    driver = webdriver.Chrome(executable_path=path)
    login_driver = LoginPage(driver)
    login_driver.open_url()
    login_driver.login_valid_user()
    print(login_driver.driver.current_url)

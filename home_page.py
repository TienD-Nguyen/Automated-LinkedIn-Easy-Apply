from page import BasePage
from search_page import SearchPage
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from locators import Locators


class HomePage(BasePage):
    def __init__(self, driver, parameters=None, url=None):
        super(HomePage, self).__init__(driver, parameters)
        self.url = url
        self.position = self.parameters.get("position", [])

    def search_job(self):
        # element = self.driver.find_element(*Locators.SEARCH_BOX)
        # element.send_keys(content)
        # element.send_keys(Keys.ENTER)
        self.enter_text(Locators.SEARCH_BOX, self.position)
        self.entering(Locators.SEARCH_BOX)
        return SearchPage(driver=self.driver, url=self.driver.current_url, parameters=self.parameters)

    def open_url(self):
        self.driver.get(self.url)
        return self


if __name__ == "__main__":
    from selenium import webdriver
    driver = webdriver.Chrome(executable_path="/Users/tiendnguyen/Desktop/chromedriver")
    url = "https://www.linkedin.com/feed/?trk=guest_homepage-basic_nav-header-signin"
    home = HomePage(driver=driver, url=url)
    home.open_url()
    home.search_job("python developer intern")

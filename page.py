from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as ec


class BasePage:
    def __init__(self, driver, parameters=None):
        self.driver = driver
        self.parameters = parameters
        # self.username = parameters["email"]
        # self.password = parameters["password"]
        # self.positions = parameters.get("positions", [])
        # self.locations = parameters.get("locations", [])
        # self.experience_level = parameters.get("experienceLevel", [])
        # self.seen_jobs = []
        # self.resume_dir = parameters["uploads"]["resume"]
        # if "coverLetter" in parameters["uploads"]:
        #     self.cover_letter_dir = parameters["uploads"]["coverLetter"]
        # else:
        #     self.cover_letter_dir = ""
        # self.output_file_directory = parameters["outputFileDirectory"]
        # self.checkboxes = parameters.get("checkboxes", [])
        # self.university_gpa = parameters["universityGPA"]
        # self.languages = parameters.get("languages", [])
        # self.industry = parameters.get("industry", [])
        # self.technology = parameters.get("technology", [])
        # self.personal_info = parameters.get("personalInfo", [])
        # self.technology_default = self.technology["default"]
        # self.industry_default = self.industry["default"]

    def click(self, by_locator):
        WebDriverWait(self.driver, 30).until(ec.visibility_of_element_located(by_locator)).click()

    def enter_text(self, by_locator, text):
        return WebDriverWait(self.driver, 20).until(ec.visibility_of_element_located(by_locator)).send_keys(text)

    def entering(self, by_locator):
        WebDriverWait(self.driver, 20).until(ec.visibility_of_element_located(by_locator)).send_keys(Keys.ENTER)

    def hover_and_click(self, by_locator):
        element = self.driver.find_element(*by_locator)
        ActionChains(self.driver).move_to_element(element).click().perform()

    def hover_to(self, by_locator):
        element = WebDriverWait(self.driver, 20).until(ec.visibility_of_element_located(by_locator))
        ActionChains(self.driver).move_to_element(element).perform()

    @staticmethod
    def select_dropdown(element, text):
        select = Select(element)
        select.select_by_visible_text(text)

    @staticmethod
    def enter_new_text(element, text):
        element.clear()
        element.send_keys(text)

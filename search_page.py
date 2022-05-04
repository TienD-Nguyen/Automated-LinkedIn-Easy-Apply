import csv
import time
import random
from selenium.common import exceptions
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import Select
from page import BasePage
from locators import Locators
from selenium.webdriver.common.by import By


class SearchPage(BasePage):
    def __init__(self, driver, parameters=None, url=None):
        super(SearchPage, self).__init__(driver, parameters)
        self.url = url
        self.location = self.parameters.get("locations", [])
        self.personal_info = self.parameters.get("personalInfo", [])
        self.experience_level = self.parameters.get("experienceLevel", [])

    def get_experience(self):
        level = 1
        for keys in self.experience_level.keys():
            if self.experience_level[keys]:
                return level
            level += 1
        return 1

    def closing_notification(self):
        closed_notification = False
        try:
            self.driver.find_element(By.CLASS_NAME, "artdeco_modal__dismiss").click()
            closed_notification = True
        except exceptions.NoSuchElementException:
            pass
        try:
            self.driver.find_element(By.CLASS_NAME, "artdeco-modal__dismiss").click()
            closed_notification = True
        except exceptions.NoSuchElementException:
            pass
        return closed_notification

    def closing_application_form(self):
        self.driver.find_element(By.CLASS_NAME, "artdeco-modal__dismiss").click()
        time.sleep(random.uniform(3, 5))
        self.driver.find_elements(By.CLASS_NAME, "artdeco-modal__confirm-dialog-btn")[1].click()
        time.sleep(random.uniform(3, 5))
        raise Exception("Failed to apply to job!")

    def apply_filter(self):
        self.click(Locators.JOBS_FILTER)
        time.sleep(4)

        self.click(Locators.EASY_APPLY_FILTER)
        time.sleep(4)

        if len(self.location) > 0:
            location_box = self.driver.find_element(*Locators.LOCATION_BOX)
            self.enter_new_text(location_box, self.location)
            self.entering(Locators.LOCATION_BOX)
        time.sleep(4)

        self.click(Locators.EXPERIENCE_FILTER)
        time.sleep(4)

        level = self.get_experience()
        experience_level = (By.ID, f"experience-{level}")
        self.hover_and_click(experience_level)
        time.sleep(4)

        self.click(Locators.FILTER_APPLY_BUTTON)

    def browsing_jobs(self):
        search_result = self.driver.find_element(By.CLASS_NAME, "jobs-search-results")
        try:
            page_numbers = self.driver.find_element(By.CLASS_NAME, "artdeco-pagination__pages--number") \
                .find_elements(By.CLASS_NAME, "artdeco-r--number")
        except exceptions.NoSuchElementException:
            jobs_list = self.driver.find_element(By.CLASS_NAME, "jobs-search-results__list") \
                .find_elements(By.CLASS_NAME, "jobs-search-results__list-item")
            if len(jobs_list) == 0:
                raise Exception("No more jobs on this page")
            for job_tile in jobs_list:
                try:
                    job_tile.click()
                    self.apply_to_job(job_tile)
                except exceptions.ElementClickInterceptedException:
                    pass
        else:
            for current_page in range(1, len(page_numbers) + 1):
                self.driver.find_element(By.XPATH, f'//button[@aria-label="Page {current_page}"]').click()
                time.sleep(5)
                jobs_list = self.driver.find_element(By.CLASS_NAME, "jobs-search-results__list")\
                    .find_elements(By.CLASS_NAME, "jobs-search-results__list-item")
                if len(jobs_list) == 0:
                    raise Exception("No more jobs on this page")
                for job_tile in jobs_list:
                    try:
                        job_tile.click()
                        self.apply_to_job(job_tile)
                    except exceptions.ElementClickInterceptedException:
                        pass

    def apply_to_job(self, job_tile):
        apply_button = None
        job_title = job_tile.find_element(By.CLASS_NAME, "job-card-list__title").text
        company = job_tile.find_element(By.CLASS_NAME, "job-card-container__company-name").text
        location = job_tile.find_element(By.CLASS_NAME, "job-card-container__metadata-item").text
        try:
            apply_button = self.driver.find_element(By.CLASS_NAME, "jobs-unified-top-card__content--two-pane")\
                .find_element(By.XPATH, '//button[contains(@class,"jobs-apply-button")]')
        except:
            print(f"The position {job_title} at {company} - {location} is no longer available OR unable to apply!")
        print(f"Applying to the position: {job_title} at {company} - {location}")
        apply_button.click()
        time.sleep(5)
        button_text = ""
        submit_application_text = "submit application"
        while submit_application_text not in button_text.lower():
            try:
                questions_form = self.driver.find_element(By.XPATH, '//div[@class="jobs-easy-apply-content"]')
            except exceptions.NoSuchElementException:
                raise Exception("Failed to apply to the position!")
            else:
                self.filling_information(questions_form)
                next_button = self.driver.find_element(By.CLASS_NAME, "artdeco-button--primary")
                button_text = next_button.text.lower()
                if submit_application_text in button_text:
                    try:
                        self.unfollowing_company()
                    except exceptions.NoSuchElementException:
                        print("Failed to unfollowing company")
                time.sleep(random.uniform(1, 3))
                next_button.click()
                time.sleep(random.uniform(2, 5))

            if "please enter a valid answer" in self.driver.page_source.lower() or "file is required" in self.driver.page_source.lower():
                print("Closing Application Window.....")
                self.closing_application_form()

        if not self.closing_notification():
            raise Exception("Could not close the applied confirmation window!")
        return True

    def filling_information(self, questions_form):
        try:
            sections = questions_form.find_elements(By.XPATH, "//div[@class='pb4']")
            for section in sections:
                label = section.find_element(By.TAG_NAME, "h3").text.lower()
                if "contact info" in label:
                    self.contact_info(section)
                elif "home address" in label:
                    self.home_address(section)
                elif "additional question" in label:
                    self.additional_questions()
                elif "resume" in label:
                    # self.upload_resume()
                    pass
                # except exceptions.NoSuchElementException:
                #     pass
        except exceptions.NoSuchElementException:
            pass

    def contact_info(self, section):
        fields = section.find_elements(*Locators.INPUT_FIELDS)
        if len(fields) > 0:
            for input_field in fields:
                label = input_field.text.lower()
                if "email address" in label:
                    print("email_address")
                    try:
                        email_picker = input_field.find_element(By.CLASS_NAME, "fb-dropdown__select")
                        self.select_dropdown(email_picker, self.personal_info["Email"])
                    except exceptions.NoSuchElementException:
                        print("Email is not found! Make sure it is exact!")
                elif "phone country code" in label:
                    print("country code")
                    try:
                        country_code_picker = input_field.find_element(By.CLASS_NAME, "fb-dropdown__select")
                        self.select_dropdown(country_code_picker, self.personal_info["Phone Country Code"])
                    except exceptions.NoSuchElementException:
                        print("Country Code is not found! Make sure it is exact!")
                elif "mobile phone number" in label:
                    print("phone number")
                    try:
                        phone_number_field = input_field.find_element(By.CLASS_NAME, "fb-single-line-text__input")
                        self.enter_new_text(phone_number_field, self.personal_info["Mobile Phone Number"])
                    except exceptions.TimeoutException:
                        print("Could not input mobile number")

    def home_address(self, section):
        try:
            fields = section.find_elements(*Locators.INPUT_FIELDS)
            if len(fields) > 0:
                for field in fields:
                    label = field.text.lower()
                    input_field = field.find_element(By.TAG_NAME, "input")
                    if "street" in label:
                        self.enter_new_text(input_field, self.personal_info["Street Address"])
                    elif "city" in label:
                        self.enter_new_text(input_field, self.personal_info["City"])
                    elif "zip" in label or "postal" in label:
                        self.enter_new_text(input_field, self.personal_info["Zip Code"])
                    elif "state" in label or "province" in label:
                        self.enter_new_text(input_field, self.personal_info["State"])
                    else:
                        pass
        except exceptions.NoSuchElementException:
            pass

    def upload_resume(self):
        resume_dir = ""
        cover_letter_dir = ""
        try:
            file_upload_elements = (By.CSS_SELECTOR, "input[name='file']")
            if len(self.driver.find_elements(*file_upload_elements)) > 0:
                input_buttons = self.driver.find_elements(*file_upload_elements)
                for upload_button in input_buttons:
                    upload_type = upload_button.find_element(By.XPATH, "..")\
                        .find_element(By.XPATH, "preceding-sibling::*")
                    if "resume" in upload_type.text.lower():
                        upload_button.send_keys(resume_dir)
                    elif "cover" in upload_type.text.lower():
                        if cover_letter_dir != "":
                            upload_button.send_keys(cover_letter_dir)
                        elif "required" in upload_type.text.lower():
                            upload_button.send_keys(resume_dir)
        except exceptions.NoSuchElementException:
            print("Failed to upload resume or cover letter")
            pass

    def additional_questions(self):
        form_questions = self.driver.find_elements(By.CLASS_NAME, "jobs-easy-apply-form-section__grouping")
        if len(form_questions) > 0:
            for question in form_questions:
                pass


    def answer_checkboxes(self, question_element):
        pass

    def answer_questions(self, question_element):
        pass

    def answer_dropdown(self, question_element):
        pass

    def answer_data(self, question_element):
        pass

    def agree_term(self, question_element):
        pass

    def unfollowing_company(self):
        try:
            follow_checkbox = self.driver.find_element(By.XPATH, '//input[@id="follow-company-checkbox"]').click()
            follow_checkbox.click()
        except exceptions.NoSuchElementException:
            pass

    def radio_select(self, element, label_text, click_last=False):
        pass

    def write_to_file(self, job_title, company_name, location):
        to_write = [company_name, job_title, location]
        file_path = "/Users/tiendnguyen/Desktop/LinkedIn_Applied.csv"

        with open(file_path, "a") as f:
            writer = csv.writer(f)
            writer.writerow(to_write)

    def open_url(self):
        self.driver.get(self.url)
        return self

    def open_new_url(self, url):
        self.driver.get(url)


if __name__ == "__main__":
    from selenium import webdriver
    path = "/Users/tiendnguyen/Desktop/chromedriver"
    driver = webdriver.Chrome(executable_path=path)
    page = SearchPage(driver, url="https://www.linkedin.com/jobs/search/?currentJobId=2899312372&f_AL=true&f_E=2&geoId=101452733&keywords=python%20developer%20intern")
    page.open_url()
    button = page.driver.find_element(By.CLASS_NAME, "jobs-unified-top-card__content--two-pane")\
        .find_element(By.XPATH, '//button[contains(@class,"jobs-apply-button")]')
    button.click()
    # sections = page.driver.find_elements(By.XPATH, '//div[@class="jobs-easy-apply-form-section__grouping"]')
    # if len(sections) > 0:
    #     for section in sections:
    #         text = section.text.lower()
    #         print(text)


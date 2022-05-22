import csv
import time
import random
from datetime import date
from selenium.common import exceptions
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from page import BasePage
from locators import Locators
from selenium.webdriver.common.by import By

RADIO_CLASS = None
DROPDOWN_CLASS = None
SINGLE_LINE_CLASS = None


class SearchPage(BasePage):
    def __init__(self, driver, parameters=None, url=None):
        super(SearchPage, self).__init__(driver, parameters)
        self.url = url
        self.location = self.parameters.get("locations", [])
        self.personal_info = self.parameters.get("personalInfo", [])
        self.experience_level = self.parameters.get("experienceLevel", [])
        self.university_gpa = self.parameters.get("universityGPA", 0)
        self.checkboxes = self.parameters.get("checkboxes", [])
        self.languages = self.parameters.get("languages", [])
        self.technologies = self.parameters.get("technology", [])
        self.industries = self.parameters.get("industry", [])
        self.output_file_directory = "/Users/tiendnguyen/Desktop/"
        self.seen_jobs = []

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
            self.driver.find_element(By.CLASS_NAME, "artdeco-toast-item__dismiss").click()
            closed_notification = True
        except exceptions.NoSuchElementException:
            pass
        return closed_notification

    def closing_application_form(self):
        self.driver.find_element(By.CLASS_NAME, "artdeco-modal__dismiss").click()
        time.sleep(random.uniform(3, 5))
        self.driver.find_elements(By.CLASS_NAME, "artdeco-modal__confirm-dialog-btn")[1].click()
        time.sleep(random.uniform(3, 5))
        print("Failed to apply to job!")

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
                    time.sleep(3)
                    if self.apply_to_job(job_tile):
                        print("Done applying for the job!!!")
                    else:
                        print("Already applied or failed to apply for the job!!!")
                except exceptions.ElementClickInterceptedException:
                    print("Could not apply for the selected job!")
        else:
            for current_page in range(1, len(page_numbers) + 1):
                self.driver.find_element(By.XPATH, f'//button[@aria-label="Page {current_page}"]').click()
                time.sleep(5)
                jobs_list = self.driver.find_element(By.CLASS_NAME, "jobs-search-results__list") \
                    .find_elements(By.CLASS_NAME, "jobs-search-results__list-item")
                if len(jobs_list) == 0:
                    raise Exception("No more jobs on this page")
                for job_tile in jobs_list:
                    try:
                        job_tile.click()
                        time.sleep(3)
                        if self.apply_to_job(job_tile):
                            print("Done applying for the job!!!")
                        else:
                            print("Already applied or failed to apply for the job!!!")
                    except exceptions.ElementClickInterceptedException:
                        print("Could not apply for the selected job!")

    def apply_to_job(self, job_tile):
        apply_button = None
        job_title = job_tile.find_element(By.CLASS_NAME, "job-card-list__title").text
        company = job_tile.find_element(By.CLASS_NAME, "job-card-container__company-name").text
        location = job_tile.find_element(By.CLASS_NAME, "job-card-container__metadata-item").text
        job_link = job_tile.find_element(By.CLASS_NAME, "job-card-list__title").get_attribute("href").split("?")[0]
        if job_link in self.seen_jobs:
            return False
        try:
            apply_button = self.driver.find_element(By.CLASS_NAME, "jobs-unified-top-card__content--two-pane") \
                .find_element(By.XPATH, '//button[contains(@class,"jobs-apply-button")]')
        except exceptions.NoSuchElementException:
            print(f"The position {job_title} at {company} - {location} is no longer available OR unable to apply!")
            return False
        print(f"Applying to the position: {job_title} at {company} - {location}")
        apply_button.click()
        time.sleep(5)
        button_text = ""
        submit_application_text = "submit application"
        while submit_application_text not in button_text.lower():
            retries = 3
            while retries > 0:
                try:
                    questions_form = self.driver.find_element(By.XPATH, '//div[@class="jobs-easy-apply-content"]')
                except exceptions.NoSuchElementException:
                    print("Failed to apply to the position!")
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

                if ("please enter a valid answer" in self.driver.page_source.lower() or
                        "file is required" in self.driver.page_source.lower()):
                    retries -= 1
                    print(f"Retrying application... Remaining attempts: {int(retries)}")
            if retries == 0:
                print("Closing Application Window.....")
                self.closing_application_form()
                self.write_to_file(file_name="LinkedIn_Failed", company_name=company, job_title=job_title,
                                   location=location, job_link=job_link)
                return False
        if not self.closing_notification():
            raise Exception("Could not close the applied confirmation window!")
        else:
            print("Writing to CSV file...")
            self.write_to_file(file_name="LinkedIn_Applied", company_name=company, job_title=job_title,
                               location=location, job_link=job_link)
        self.seen_jobs.append(job_link)
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
                elif "additional questions" in label:
                    self.additional_questions(section)
                elif "resume" in label:
                    # self.upload_resume()
                    pass
        except exceptions.NoSuchElementException:
            pass

    def contact_info(self, section):
        fields = section.find_elements(*Locators.INPUT_FIELDS)
        if len(fields) > 0:
            for input_field in fields:
                label = input_field.text.lower()
                if "email address" in label:
                    try:
                        email_picker = input_field.find_element(By.CLASS_NAME, "fb-dropdown__select")
                        self.select_dropdown(email_picker, self.personal_info["Email"])
                    except exceptions.NoSuchElementException:
                        print("Email is not found! Make sure it is exact!")
                elif "phone country code" in label:
                    try:
                        country_code_picker = input_field.find_element(By.CLASS_NAME, "fb-dropdown__select")
                        self.select_dropdown(country_code_picker, self.personal_info["Phone Country Code"])
                    except exceptions.NoSuchElementException:
                        print("Country Code is not found! Make sure it is exact!")
                elif "mobile phone number" in label:
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
                    upload_type = upload_button.find_element(By.XPATH, "..") \
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

    def additional_questions(self, section):
        questions_form = section.find_elements(By.CLASS_NAME, "jobs-easy-apply-form-section__grouping")
        if len(questions_form) > 0:
            for question in questions_form:
                if self.answer_questions(question):
                    continue
                elif self.answer_checkboxes(question):
                    continue
                elif self.answer_dropdown(question):
                    continue
                elif self.answer_date(question):
                    continue
                else:
                    self.agree_term(question)

    def answer_checkboxes(self, question_element):
        print("I'm answering checkboxes questions")
        try:
            question = question_element.find_element(*Locators.RADIO_FIELD)
            question_text = question.find_element(*Locators.QUESTION_TEXT).text.lower()
            radio_buttons = question.find_elements(By.CLASS_NAME, "fb-radio")
        except exceptions.NoSuchElementException:
            return False
        else:
            radio_options = [option.text.lower() for option in radio_buttons]
            answer = ""
            if "driver's license" in question_text:
                answer = self.checkboxes["driversLicense"]
            elif ("gender" in question_text or "veteran" in question_text or
                  "race" in question_text or "disability" in question_text or "latino" in question_text):
                answer = ""
                for option in radio_options:
                    if ("prefer" in option.lower() or "decline" in option.lower() or
                            "don't" in option.lower() or "specified" in option.lower() or
                            "none" in option.lower()):
                        answer = option
                if answer == "":
                    answer = radio_options[-1]
            elif "north korea" in question_text:
                answer = "no"
            elif "sponsor" in question_text:
                answer = self.checkboxes["requireVisa"]
            elif "authorized" in question_text or "authorised" in question_text or "legally" in question_text:
                answer = self.checkboxes["legallyAutorised"]
            elif "urgent" in question_text:
                answer = self.checkboxes["urgentFill"]
            elif "commuting" in question_text:
                answer = self.checkboxes["commute"]
            elif "background check" in question_text:
                answer = self.checkboxes["backgroundCheck"]
            elif "level of education" in question_text:
                for degree in self.checkboxes["degreeCompleted"]:
                    if degree.lower() in question_text:
                        answer = "yes"
                        break
            elif "data retention" in question_text:
                answer = "no"
            else:
                answer = radio_options[-1]
            select_option = None
            for idx, radio_button in enumerate(radio_buttons):
                if answer.lower() == "yes" and answer in radio_button.text.lower():
                    select_option = radio_buttons[idx]
            if not select_option:
                select_option = radio_buttons[-1]
            self.radio_select(select_option, answer, len(radio_buttons) > 2)
            return True

    def answer_questions(self, question_element):
        print("I'm answering single line questions")
        try:
            question = question_element.find_element(*Locators.INPUT_FIELDS)
            question_text = question.find_element(*Locators.QUESTION_TEXT).text.lower()
            text_field_visible = False
            try:
                text_field = question.find_element(By.CLASS_NAME, "fb-single-line-text__input")
                text_field_visible = True
            except exceptions.NoSuchElementException:
                text_field = question.find_element(By.CLASS_NAME, "fb-textarea")
                text_field_visible = True
            if not text_field_visible:
                text_field = question.find_element(By.CLASS_NAME, "multi-line-text__input")
        except exceptions.NoSuchElementException:
            return False
        else:
            text_field_type = text_field.get_attribute("name").lower()
            if "numeric" in text_field_type:
                text_field_type = "numeric"
            elif "text" in text_field_type:
                text_field_type = "text"

            input_text = ""
            if "experience do you currently have" in question_text:
                input_text = self.industries["default"]
                for industry in self.industries:
                    if industry.lower() in question_text:
                        input_text = self.industries[industry]
                        break
            elif "many years of work experience do you have using" in question_text:
                input_text = self.technologies["default"]
                for technology in self.technologies:
                    if technology.lower() in question_text:
                        input_text = self.technologies[technology]
                        break
            elif "grade point average" in question_text:
                input_text = self.university_gpa
            elif "first name" in question_text:
                input_text = self.personal_info["First Name"]
            elif "last name" in question_text:
                input_text = self.personal_info["Last Name"]
            elif "name" in question_text:
                input_text = self.personal_info["First Name"] + " " + self.personal_info["Last Name"]
            elif "phone" in question_text:
                input_text = self.personal_info["Mobile Phone Number"]
            elif "linkedin" in question_text:
                input_text = self.personal_info["LinkedIn"]
            elif "website" in question_text or "github" in question_text or "portfolio" in question_text:
                input_text = self.personal_info["Website"]
            elif "salary expectations" in question_text:
                input_text = "0"
            else:
                if text_field_type == "numeric":
                    input_text = 0
                else:
                    input_text = " "
            self.enter_new_text(text_field, input_text)
            return True

    def answer_dropdown(self, question_element):
        print("I'm answering dropdown questions")
        try:
            question = question_element.find_element(*Locators.INPUT_FIELDS)
            question_text = question.find_element(*Locators.QUESTION_TEXT).text.lower()
            dropdown_field = question.find_element(By.XPATH, '//select[contains(@class,"fb-dropdown__select")]')
        except exceptions.NoSuchElementException:
            return False
        else:
            select = Select(dropdown_field)

            options = [option.text for option in select.options]
            print(options)

            if "proficiency" in question_text:
                proficiency = "Conversational"
                for language in self.languages:
                    if language.lower() in question_text:
                        proficiency = self.languages[language]
                        break
                self.select_dropdown(dropdown_field, proficiency)
            elif "country code" in question_text:
                self.select_dropdown(dropdown_field, self.personal_info["Phone Country Code"])
            elif "north korea" in question_text:
                choice = ""
                for option in options:
                    if "no" in option.lower():
                        choice = option
                if choice == "":
                    choice += options[-1]
                self.select_dropdown(dropdown_field, choice)
            elif "sponsor" in question_text:
                choice = self.choice_selection(options=options, term="requireVisa")
                self.select_dropdown(dropdown_field, choice)
            elif "authorized" in question_text or "authorised" in question_text or "citizenship" in question_text:
                choice = self.choice_selection(options=options, term="legallyAuthorised")
                self.select_dropdown(dropdown_field, choice)
            elif ("gender" in question_text or "veteran" in question_text or
                  "race" in question_text or "disability" in question_text or
                  "latino" in question_text):
                choice = ""
                for option in options:
                    if ("prefer" in option.lower() or "decline" in option.lower() or
                            "don't" in option.lower() or "specified" in option.lower() or
                            "none" in option.lower()):
                        choice += option
                if choice == "":
                    choice = options[-1]
                self.select_dropdown(dropdown_field, choice)
            else:
                choice = ""
                for option in options:
                    if "yes" in option.lower():
                        choice = option
                if choice == "":
                    choice = options[-1]
                self.select_dropdown(dropdown_field, choice)
                return True

    @staticmethod
    def answer_date(question_element):
        try:
            date_picker = question_element.find_element(By.CLASS_NAME, "artdeco-datepicker__input")
        except exceptions.NoSuchElementException:
            return False
        else:
            date_picker.clear()
            date_picker.send_keys(date.today().strftime("%m/%d/%y"))
            time.sleep(2)
            date_picker.send_keys(Keys.RETURN)
            time.sleep(2)
            return True

    def agree_term(self, question_element):
        try:
            question = question_element.find_element(*Locators.FORM_ELEMENT)
        except exceptions.NoSuchElementException:
            pass
        else:
            clickable_checkbox = question.find_element(By.TAG_NAME, "label")
            clickable_checkbox.click()

    def choice_selection(self, options, term):
        answer = self.checkboxes[term]
        choice = ""
        for option in options:
            if answer and "yes" in option.lower():
                choice = option
            elif not answer and "no" in option.lower():
                choice = option
        if choice == "":
            choice = options[-1]
        return choice

    def unfollowing_company(self):
        try:
            follow_checkbox = self.driver.find_element(By.XPATH, '//input[@id="follow-company-checkbox"]').click()
            follow_checkbox.click()
        except exceptions.NoSuchElementException:
            pass

    def radio_select(self, element, label_text, click_last=False):
        label = element.find_element(By.TAG_NAME, "label")
        if label_text in label.text.lower() or click_last == True:
            label.click()
        else:
            pass

    def write_to_file(self, file_name, job_title, company_name, location, job_link):
        to_write = [company_name, job_title, location, job_link]
        file_path = self.output_file_directory + file_name + ".csv"

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
    page = SearchPage(driver,
                      url="https://www.linkedin.com/jobs/search/?currentJobId=2899312372&f_AL=true&f_E=2&geoId=101452733&keywords=python%20developer%20intern")
    page.open_url()
    button = page.driver.find_element(By.CLASS_NAME, "jobs-unified-top-card__content--two-pane") \
        .find_element(By.XPATH, '//button[contains(@class,"jobs-apply-button")]')
    button.click()
    # sections = page.driver.find_elements(By.XPATH, '//div[@class="jobs-easy-apply-form-section__grouping"]')
    # if len(sections) > 0:
    #     for section in sections:
    #         text = section.text.lower()
    #         print(text)

from selenium.webdriver.common.by import By


class Locators:
    # Login Page Locators
    USERNAME_INPUT = (By.ID, "username")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON = (By.CSS_SELECTOR, ".login__form_action_container")

    # Home Page Locators
    SEARCH_BOX = (By.XPATH, '//*[@id="global-nav-typeahead"]/input')
    LOCATION_BOX = (By.XPATH, '//div[contains(@class, "jobs-search-box__input--location")]'
                              '//input[@class="jobs-search-box__text-input"]')

    # Search Page Locators
    JOBS_FILTER = (By.XPATH, '//button[@aria-label="Jobs"]')
    EXPERIENCE_FILTER = (By.XPATH, '//div[@class="search-reusables__filter-trigger-and-dropdown"]'
                                   '//button[text()="Experience Level"]')
    EXPERIENCE_LEVEL = (By.ID, 'experience-2')
    FILTER_APPLY_BUTTON = (By.XPATH, '//div[@id="hoverable-outlet-experience-level-filter-value"]'
                                     '//button[@data-control-name="filter_show_results"]')
    EASY_APPLY_FILTER = (By.XPATH, '//button[@aria-label="Easy Apply filter."]')

    # Applying
    EASY_APPLY_BUTTON = (By.CSS_SELECTOR, ".jobs-s-apply button")
    INPUT_FIELDS = (By.XPATH, '//div[contains(@class,"jobs-easy-apply-form-element")]')
